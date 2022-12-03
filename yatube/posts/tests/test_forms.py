import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Post, Group


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_user')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='description_of_test_group'
        )

        cls.different_droup = Group.objects.create(
            title='test_group_diff',
            slug='test_slug_diff',
            description='description_of_test_group_diff'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_and_edit_post(self):
        """
        Forms: формы posts:post_create и posts.post_edit работают корректно.
        """
        posts_count = Post.objects.count()

        # Потом созданный здесь пост будем использовать в этом же
        # методе для проверки post_edit, чтобы не повторять код

        image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=image,
            content_type='image/gif'
        )

        form_data = {
            'text': 'Test_post',
            'author': self.user,
            'group': self.group.pk,
            'image': uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        # Блок для проверки post_create
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': f'{self.user.username}'}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test_post',
                author=self.user,
                group=self.group,
            ).exists()
        )

        # Блок проверки post_edit
        post = Post.objects.get(text=form_data['text'])
        post_id = post.id
        # В form_data обазятельно указываем только те поля, которые собираемся
        # изменить тестовым запросом. Благодаря этому, сможем проверять,
        # внесены ли изменения в БД, даже если меняются не все поля Поста
        form_data = {
            'text': 'Edited_Test_post',
            'group': self.different_droup.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )

        fields = [
            'text',
            'author',
            'group',
            'image',
        ]

        # Создаем список полей, которые должны были быть изменены
        edited_fields = list()
        for field in fields:
            if field in form_data.keys():
                edited_fields.append(field)

        # Проверяем, были ли внесены изменения БД в поля из
        # списка edited_fields
        for field in edited_fields:
            with self.subTest(field=field):
                self.assertNotEqual(
                    getattr(post, field),
                    getattr(Post.objects.get(pk=post_id), field)
                )

    def test_comments(self):
        """
        Posts: Комментировать посты может только авторизованный пользователь.
        """

        post = Post.objects.create(
            text='Test_post',
            author=self.user,
            group=self.group
        )
        url = reverse('posts:add_comment', kwargs={'post_id': f'{post.id}'})
        post_page = reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{post.id}'}
        )

        comments_count = post.comments.count()

        form_data = {
            'text': 'Test_comment',
        }

        # Попытка создать комментарий неавторизованным пользователем
        response = self.guest_client.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertEqual(post.comments.count(), comments_count)

        # Попытка создать комментарий авторизованным пользователем
        response = self.authorized_client.post(
            url,
            data=form_data,
            follow=True
        )

        self.assertEqual(post.comments.count(), comments_count + 1)

        # Создаенный комментарий появляется на странице поста
        response = self.guest_client.get(post_page)
        first_comment = response.context['comments'][0]
        self.assertEqual(first_comment, post.comments.get(text='Test_comment'))

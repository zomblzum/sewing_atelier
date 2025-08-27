from django.db import models
from django.core.validators import RegexValidator
import random
from django.contrib.auth.models import User

class OrderStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Название статуса")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет")
    is_default = models.BooleanField(default=False, verbose_name="Статус по умолчанию")

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"
        unique_together = ['user', 'name']  # Уникальное название для каждого пользователя

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Телефон должен быть в формате: '+999999999'. Максимум 15 цифр."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Телефон"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказчик"
        verbose_name_plural = "Заказчики"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.phone}) - {self.user.username}"

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=100, verbose_name="Название категории")
    default_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена по умолчанию"
    )
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        unique_together = ['user', 'name']  # Уникальное название для каждого пользователя
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    title = models.CharField(max_length=200, verbose_name="Название заказа")
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Заказчик"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    status = models.ForeignKey(
        OrderStatus,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Статус"
    )
    planned_date = models.DateField(null=True, blank=True, verbose_name="Планируемая дата")
    planned_minutes = models.PositiveIntegerField(default=60, verbose_name="Планируемые минуты")
    planned_start_time = models.TimeField(null=True, blank=True, verbose_name="Время начала")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет в планере")
    order_in_day = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Порядковый номер в дне",
        default=None
    )    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def save(self, *args, **kwargs):
        if not self.status:
            # Устанавливаем статус по умолчанию для текущего пользователя
            default_status = OrderStatus.objects.filter(user=self.user, is_default=True).first()
            if default_status:
                self.status = default_status
        
        if not self.color or self.color == '#007bff':
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A826', '#6A0572', 
                     '#AB83A1', '#5C80BC', '#4CB944', '#E2B1B1', '#7D70BA']
            self.color = random.choice(colors)
        
        super().save(*args, **kwargs)

class PlannerSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    hours_per_day = models.PositiveIntegerField(default=8, verbose_name="Рабочих часов в день")
    work_days = models.CharField(
        max_length=13, 
        default='1,2,3,4,5',
        verbose_name="Рабочие дни (1-ПН,7-ВС)",
        help_text="Через запятую, где 1 - понедельник, 7 - воскресенье"
    )

    class Meta:
        verbose_name = "Настройка планера"
        verbose_name_plural = "Настройки планера"

    def __str__(self):
        return f"Настройки планера ({self.user.username})"
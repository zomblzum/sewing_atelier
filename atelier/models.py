from django.db import models
from django.core.validators import RegexValidator
import random

class OrderStatus(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название статуса")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет")
    is_default = models.BooleanField(default=False, verbose_name="Статус по умолчанию")

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return self.name

class Category(models.Model):
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
    
    def __str__(self):
        return self.name    

class Customer(models.Model):
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
        return f"{self.last_name} {self.first_name} ({self.phone})"

class Order(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название заказа")
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Заказчик"
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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Категория"
    )    
    planned_date = models.DateField(null=True, blank=True, verbose_name="Планируемая дата")
    color = models.CharField(max_length=7, default='#007bff', verbose_name="Цвет в планере")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    planned_minutes = models.PositiveIntegerField(default=60, verbose_name="Планируемые минуты")
    order_in_day = models.PositiveIntegerField(null=True, blank=True, verbose_name="Порядок в дне")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Если указана категория и цена не была изменена вручную, устанавливаем цену из категории
        if self.category and not self._state.adding:
            original = Order.objects.get(pk=self.pk)
            if original.price == original.category.default_price if original.category else 0:
                self.price = self.category.default_price
        elif self.category and self._state.adding:
            self.price = self.category.default_price
        
        if not self.status:
            default_status = OrderStatus.objects.filter(is_default=True).first()
            if default_status:
                self.status = default_status
        
        if not self.color or self.color == '#007bff':
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A826', '#6A0572', 
                     '#AB83A1', '#5C80BC', '#4CB944', '#E2B1B1', '#7D70BA']
            self.color = random.choice(colors)
        
        super().save(*args, **kwargs)

class PlannerSettings(models.Model):
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
        return f"Настройки планера ({self.hours_per_day} часов/день)"
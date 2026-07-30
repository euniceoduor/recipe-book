from django.db import models
from django.contrib.auth.models import User

from urllib.parse import urljoin
from pathlib import Path

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank = True)
    is_private = models.BooleanField(default = False)
    first_name = models.CharField(max_length=20, blank=True, default = "")
    last_name = models.CharField(max_length=20, blank=True, default = "")
    profile_picture = models.ImageField(upload_to='profile_photos/', blank=True, null = True)


    def __str__(self):
        return self.user.username



class Recipe(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=400, help_text="Describe the dish")
    cook_time = models.CharField(max_length = 20)
    serves = models.CharField(max_length=20)
    is_private = models.BooleanField(default= False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cover_photo(self):
        first_photo = self.photos.first()
        if not first_photo:
            return None
        return first_photo.image.url

    

    def __str__(self):
        return self.title
    
class Ingredient(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.CharField(max_length=10, blank=True)
    unit =  models.CharField(max_length=10,blank = True)
    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"
    
class InstructionsStep(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='instructions',on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f" Step{self.step_number} for {self.recipe.title}: {self.description}"
    
class RecipePhoto(models.Model):
    recipe = models.ForeignKey(Recipe, related_name = 'photos', on_delete = models.CASCADE)
    image = models.ImageField(upload_to='recipe_photos/')

    def __str__(self):
        return f"Photo for {self.recipe.title}"
    
class Comment(models.Model):
    recipe= models.ForeignKey(Recipe, related_name="comments", on_delete=models.CASCADE)
    profile= models.ForeignKey(Profile, related_name="comments", on_delete=models.CASCADE)
    comment= models.TextField(max_length=400)
    created_at= models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.user.username} {self.comment}"
    

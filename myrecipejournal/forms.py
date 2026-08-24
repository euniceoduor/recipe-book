from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, InstructionsStep, RecipePhoto, Comment, Profile
from django.forms import inlineformset_factory

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'serves', 'cook_time', 'is_private']

class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'quantity','unit']

        labels = {
            "name": "Ingredient",
            "quantity": "Qty",
            "unit": "Unit"
        }

        widgets = {
            "name": forms.TextInput(attrs={"placeholder":"e.g. Sugar"}),
            "quantity": forms.TextInput(attrs={"placeholder": "e.g. 1"}),
            "unit": forms.TextInput(attrs={"placeholder": "e.g. cup"}),
        }

IngredientFormSet =inlineformset_factory(
    Recipe, Ingredient, 
    form= IngredientForm, extra = 0, can_delete= True
)
        
InstructionFormSet = inlineformset_factory(
    Recipe, InstructionsStep,
    fields = ['step_number', 'description'],extra = 0,
    can_delete = True
)

class RecipePhotoForm(forms.ModelForm):
    class Meta:
        model = RecipePhoto
        fields = ['image']
        widgets = {
                'image': forms.ClearableFileInput(attrs = {
                    'accept':'image/*',
                })
        }

PhotoFormSet = inlineformset_factory(
    Recipe, RecipePhoto,
    form=RecipePhotoForm,
    fields = ['image'], extra = 0,
    can_delete= True
)
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields=['first_name', 'last_name', 'profile_picture','bio', 'is_private' ]

        widgets ={
            'first_name': forms.TextInput(attrs ={
                'placeholder':'First Name',
            }),
            'last_name': forms.TextInput(attrs ={
                'placeholder':'Last Name',
            }),
            'bio': forms.TextInput(attrs ={
                'placeholder':'Tell us what you like to eat, cook, bake, snack and which recipes you will be sharing and enjoying...', 'rows': 3,
            }),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1','password2']

class CommentForm(forms.ModelForm):
    class Meta:
        model=Comment
        fields=["comment"]
        widgets = {
            "comment": forms.Textarea(attrs= {
                "rows":2,
                "placeholder":"Add a comment..."
            })
        }
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Recipe, Ingredient, InstructionsStep, RecipePhoto, Comment, Profile, PostComment
from django.forms import inlineformset_factory
from myrecipejournal.data import MEASUREMENTS

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
            "quantity": forms.NumberInput(attrs={"placeholder": "e.g. 1.50", "step":"0.01"}),
            "unit": forms.Select(choices= MEASUREMENTS)
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
                    'multiple':False,
                })
        }

PhotoFormSet = inlineformset_factory(
    Recipe, RecipePhoto,
    form=RecipePhotoForm,
    fields = ['image'], extra = 0,
    can_delete= True
)
        
class ProfileForm(forms.ModelForm):

    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "placeholder": "Username",
        })
    )
     
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
            'profile_picture': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'capture': 'environment',   # opens camera first on mobile
                'multiple': False,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Pre-fill username
        if self.user:
            self.fields["username"].initial = self.user.username

    def clean_username(self):
        username = self.cleaned_data["username"]
        # Prevent duplicate usernames
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)

        # Save username to the User model
        user = self.user
        user.username = self.cleaned_data["username"]

        if commit:
            user.save()
            profile.save()

        return profile


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

class PostCommentForm(forms.ModelForm):
    class Meta:
        model=PostComment
        fields=["comment"]
        widgets = {
            "comment": forms.Textarea(attrs= {
                "rows":2,
                "placeholder":"Add a comment..."
            })
        }
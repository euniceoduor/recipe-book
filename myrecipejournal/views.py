from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

#Creating users
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout

from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q

from .models import Recipe, RecipePhoto, Ingredient,Profile
from .forms import ProfileForm, RecipeForm, SignUpForm, IngredientFormSet, InstructionFormSet, PhotoFormSet, CommentForm

#To enable pdfs
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


from pathlib import Path
from django.conf import settings

#SIGNUP
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already registered.")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

#logout functions
def logout_view(request):
    logout(request)
    return redirect("recipe_list")


# Create your views here.

def about_page(request):
    return render(request, "myrecipejournal/about.html")

def user_is_profile_owner(user, profile):
    return profile.user == user

@login_required
def profile_page(request):
    model= Profile
    profile, created = Profile.objects.get_or_create(user=request.user)

    context = {
        "profile": profile,
        "is_owner": user_is_profile_owner(request.user, profile),
    }

    return render(request, "myrecipejournal/profile.html", context)

@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance = profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
        
    else:
        form=ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "myrecipejournal/profile_edit.html", context)


        

@login_required
def recipe_list_user(request):
    recipes = request.user.recipes.all()
    return render(request, "myrecipejournal/recipe_list.html", {"recipes": recipes})


# List all recipes
class RecipeListView(ListView):
    model = Recipe
    template_name = 'myrecipejournal/recipe_list.html'
    context_object_name = 'recipes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["name"] = user.username if user.is_authenticated else "foodie"
        return context

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Recipe.objects.filter(
                Q(is_private=False) | Q(owner = user)).order_by('-created_at')
        return Recipe.objects.filter(is_private = False).order_by('-created_at')

#I found a challenge in that I need to be able to add, save or delete an individual ingredient

@require_POST
def save_ingredient(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)

    ingredient_id= request.POST.get("id")
    name = request.POST.get("name")
    quantity = request.POST.get("quantity")

    if ingredient_id:
        ingredient = Ingredient.objects.get(id=ingredient_id, recipe = recipe)
    else:
        ingredient = Ingredient(recipe=recipe)

    ingredient.name = name
    ingredient.quantity = quantity
    ingredient.save()

    return JsonResponse({
        "id": ingredient_id,
        "name": ingredient.name,
        "quantity": ingredient.quantity,
    })

@require_POST
def delete_ingredient(request, ingredient_id):
    Ingredient.objects.filter(id=ingredient_id).delete()
    return JsonResponse({"deleted": True})

def user_is_recipe_owner(user, recipe):
    return recipe.owner == user

#View cute version of recipe
class RecipePrintView(DetailView):
    model= Recipe
    context_object_name = 'recipe'
    template_name = 'myrecipejournal/recipe_view.html'

    

    test_path = Path(settings.MEDIA_ROOT) / "test.txt"
    with open(test_path, "w") as f:
        f.write("hello railway")

    print("Wrote test file:", test_path)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.get_object()

        context["photos"] = recipe.photos.all()
        context["ingredients"] = recipe.ingredients.all()
        context["instructions"] = recipe.instructions.all()
        context["comments"] =recipe.comments.order_by("-created_at")
        context["comment_form"] = CommentForm()
        context["is_owner"] = user_is_recipe_owner(self.request.user, recipe)

        return context
    
    def post(self,request,*args,**kwargs):
        """Section handles posting a new comment"""
        self.object = self.get_object()
        recipe = self.object

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.profile = request.user.profile
            comment.save()

        return redirect("recipe_view", pk=recipe.pk)

def get_recipe_card_context(request, recipe_id):
    

    recipe = get_object_or_404(Recipe, id = recipe_id)

    photos = recipe.photos.all()
    ingredients = recipe.ingredients.all()
    instructions = recipe.instructions.all()
    comments =recipe.comments.order_by("-created_at")
    comment_form = CommentForm()
    is_owner = user_is_recipe_owner(request.user, recipe)
  
    
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.recipe = recipe
        comment.profile = request.user.profile
        comment.save()

    context = {
        "recipe": recipe,
        "photos": photos,
        "ingredients": ingredients,
        "instructions": instructions,
        "comments": comments,
        "comment_form":comment_form,
        "is_owner": is_owner
    }

    return context

def RecipePrintPDF(request, recipe_id):
    recipe = get_object_or_404(Recipe, id = recipe_id)

    context = get_recipe_card_context(request, recipe_id)

    #Get first_photo
    first_photo = recipe.photos.first()
    if first_photo:
        cover_photo = Path(first_photo.image.path).as_uri()
    else:
        cover_photo = None

    context["cover_photo"] = cover_photo
    
    recipe_title = recipe.title.replace(" ", "_")
    owner = recipe.owner.username
    filename= f"{recipe_title}_by_{owner}.pdf"

    html = render_to_string("myrecipejournal/recipe_card_pdf.html", context)

    response = HttpResponse( content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"{filename}"'
    pisa.CreatePDF(html, dest=response)

    return response


class RecipeEditView(DetailView):
    model= Recipe
    context_object_name = 'recipe'
    template_name = 'myrecipejournal/recipe_edit.html'
    

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        recipe = self.get_object()
        context['form'] = RecipeForm(instance=recipe)

         # If POST, preserve submitted data
        if self.request.method == "POST":
            context['form'] = RecipeForm(self.request.POST, instance = recipe)
            context['photo_formset'] = PhotoFormSet(self.request.POST, self.request.FILES, instance=recipe)
            context['ingredient_formset'] = IngredientFormSet(self.request.POST, instance=recipe)
            context['instruction_formset'] = InstructionFormSet(self.request.POST, instance=recipe)
        else:
            # Initial formsets for GET
            context['photo_formset'] = PhotoFormSet(instance=recipe)
            context['ingredient_formset'] = IngredientFormSet(instance=recipe)
            context['instruction_formset'] = InstructionFormSet(instance=recipe)

        # Pass existing related objects for display
        context['photos'] = recipe.photos.all()
        context['ingredients'] = recipe.ingredients.all()
        context['instructions'] = recipe.instructions.all()
        
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle form submission and redirect back to detail view."""
        self.object = self.get_object()
        recipe = self.object

        if 'save_photos' in request.POST:
            photo_formset = PhotoFormSet(request.POST, request.FILES, instance=recipe)
            if photo_formset.is_valid():
                photo_formset.save()
            return redirect('recipe_edit', pk=recipe.pk)

                    
        elif 'save_ingredients' in request.POST:
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            if ingredient_formset.is_valid():
                ingredient_formset.save()
            return redirect('recipe_edit', pk=recipe.pk)

        elif 'save_instructions' in request.POST:
            instruction_formset = InstructionFormSet(request.POST, instance=recipe)
            if instruction_formset.is_valid():
                instruction_formset.save()
            return redirect('recipe_edit', pk=recipe.pk)
        
        elif 'save_all' in request.POST:
            #Save all formsets at once
            form = RecipeForm(request.POST, instance=recipe)
            photo_formset = PhotoFormSet(request.POST, request.FILES, instance=recipe)
            ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
            instruction_formset = InstructionFormSet(request.POST, instance=recipe)

            if (form.is_valid() and photo_formset.is_valid() and 
                ingredient_formset.is_valid() and 
                instruction_formset.is_valid()):

                form.save()
                photo_formset.save()
                ingredient_formset.save()
                instruction_formset.save()

            return redirect('recipe_view', pk=recipe.pk)

        return redirect('recipe_edit', pk=recipe.pk)



# Create a new recipe
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'myrecipejournal/recipe_edit.html'
    success_url = reverse_lazy('recipe_list')

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        #creates empty formsets for a new recipe
        context['photo_formset'] = PhotoFormSet(prefix = 'photos')
        context['ingredient_formset'] = IngredientFormSet(prefix='ingredients')
        context['instruction_formset'] = InstructionFormSet(prefix='instructions')

        #Shows empty lists for display
        context['photos'] = []
        context['ingredients']=[]
        context['instructions']=[]

        return context
       
    def post(self, request, *args, **kwargs):
        
        form = self.form_class(request.POST)
        ingredient_formset = IngredientFormSet(request.POST, prefix='ingredients')
        instruction_formset = InstructionFormSet(request.POST, prefix='instructions')
        photo_formset = PhotoFormSet(request.POST, request.FILES, prefix='photos')

        if (form.is_valid() and ingredient_formset.is_valid() and instruction_formset.is_valid() and photo_formset.is_valid()):
            form.instance.owner = request.user
            recipe = form.save()

            #Attaching formsets to the new recipe
            ingredient_formset.instance = recipe
            ingredient_formset.save()

            instruction_formset.instance = recipe
            instruction_formset.save()

            photo_formset.instance = recipe
            photo_formset.save()


            #Go to print view after creating
            return redirect('recipe_view', pk = recipe.pk)
        
        #If invalid, render with errors
        return render(request, self.template_name, {
            'form': form,
            'ingredient_formset': ingredient_formset,
            'instruction_formset': instruction_formset,
            'photo_formset': photo_formset,
            'photos': [],
            'ingredients': [],
            'instructions':[],
        })


# Delete a recipe
class RecipeDeleteView(LoginRequiredMixin, DeleteView):
    model = Recipe
    template_name = 'myrecipejournal/recipe_confirm_delete.html'

    def get_success_url(self):

        return reverse_lazy('recipe_list')

    

#Delete a recipe photo
def delete_photo(request, photo_id):
    photo = get_object_or_404(RecipePhoto, id = photo_id)

    # Optional: Ensure only the recipe owner can delete
    if request.user != photo.recipe.owner:
        messages.error(request, "You do not have permission to delete this photo.")
        return redirect('recipe_edit', pk=photo.recipe.id)

    if request.method == 'POST':
        photo.delete()
        messages.success(request, "Photo deleted successfully.")
        return redirect('recipe_edit', pk=photo.recipe.id)
    
    return redirect('recipe_edit', pk=photo.recipe.id)

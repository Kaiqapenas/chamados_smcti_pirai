from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.db.models import Max
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import ItemEstoque, CategoriaItem, ItemImagem, MovimentacaoEstoque
from .forms import ItemEstoqueForm, CategoriaItemForm, MovimentacaoEstoqueForm

# 🔹 LISTVIEW ESTOQUE
class EstoqueListView(LoginRequiredMixin, ListView):
    model = ItemEstoque
    template_name = "estoque/lista.html"
    context_object_name = "estoques"

# 🔹 CREATE ESTOQUE
class EstoqueCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ItemEstoqueForm()
        return render(request, "estoque/form.html", {"form": form})

    def post(self, request):
        form = ItemEstoqueForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            # salvar imagens separadamente (não é campo do ModelForm)
            imagens = request.FILES.getlist("imagens")
            for index, img in enumerate(imagens):
                ItemImagem.objects.create(
                    produto=item, imagem=img,
                    ordem=index, is_principal=(index == 0)
                )
            return redirect("estoque:editar", pk=item.id)
        return render(request, "estoque/form.html", {"form": form})

# 🔹 UPDATE ESTOQUE
class EstoqueUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        item = get_object_or_404(ItemEstoque, pk=pk)
        form = ItemEstoqueForm(instance=item)
        
        form.fields['quantidade'].disabled = True
        
        return render(request, "estoque/form.html", {"form": form, "item": item})

    def post(self, request, pk):
        item = get_object_or_404(ItemEstoque, pk=pk)
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item)

        if form.is_valid():
            form.save()

            # 🔥 1. REMOVER IMAGENS (se enviado no form)
            ids_remover = request.POST.getlist("remover_imagens")
            if ids_remover:
                ItemImagem.objects.filter(id__in=ids_remover, produto=item).delete()

            # 🔥 2. DEFINIR IMAGEM PRINCIPAL
            imagem_principal_id = request.POST.get("imagem_principal")
            if imagem_principal_id:
                item.imagens.update(is_principal=False)
                ItemImagem.objects.filter(id=imagem_principal_id, produto=item).update(is_principal=True)

            # 🔥 3. ADICIONAR NOVAS IMAGENS
            imagens = request.FILES.getlist("imagens")

            if imagens:
                ultima_ordem = item.imagens.aggregate(
                    max_ordem=Max('ordem')
                )['max_ordem']

                if ultima_ordem is None:
                    ultima_ordem = 0
                else:
                    ultima_ordem += 1

                for index, img in enumerate(imagens):
                    ItemImagem.objects.create(
                        produto=item,
                        imagem=img,
                        ordem=ultima_ordem + index,
                        is_principal=False
                    )

            return redirect("estoque:editar", pk=item.id)

        return render(request, "estoque/form.html", {"form": form, "item": item})

# 🔹 DELETE ESTOQUE
class EstoqueDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk):  # ⚠️ não recomendado
        item = get_object_or_404(ItemEstoque, pk=pk)
        item.delete()
        return redirect("estoque:lista")

    def post(self, request, pk):
        item = get_object_or_404(ItemEstoque, pk=pk)
        item.delete()
        return redirect("estoque:lista")

# 🔹 LISTVIEW CATEGORIA
class CategoriaEstoqueListView(LoginRequiredMixin, ListView):
    model = CategoriaItem
    template_name = "estoque/lista_categoria.html"
    context_object_name = "categorias"
    
# 🔹 CREATE CATEGORIA
class CategoriaEstoqueCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CategoriaItemForm()
        return render(request, "estoque/form_categoria.html", {"form": form})

    def post(self, request):
        form = CategoriaItemForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("estoque:categoria_lista")

        return render(request, "estoque/form_categoria.html", {"form": form})

# 🔹 UPDATE CATEGORIA
class CategoriaEstoqueUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        form = CategoriaItemForm(instance=categoria)

        return render(request, "estoque/form_categoria.html", {
            "form": form,
            "categoria": categoria
        })

    def post(self, request, pk):
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        form = CategoriaItemForm(request.POST, instance=categoria)

        if form.is_valid():
            form.save()
            return redirect("estoque:categoria_lista")

        return render(request, "estoque/form_categoria.html", {
            "form": form,
            "categoria": categoria
        })

# 🔹 DELETE CATEGORIA
class CategoriaEstoqueDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):  # ⚠️ não recomendado
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        categoria.delete()
        return redirect("estoque:categoria_lista")
    def post(self, request, pk):
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        categoria.delete()
        return redirect("estoque:categoria_lista")
 
# 🔹 LISTVIEW MOVIMENTAÇÃO ESTOQUE
class MovimentacaoEstoqueListView(LoginRequiredMixin, ListView):
    model = MovimentacaoEstoque
    template_name = "estoque/lista_movimentacao.html"
    context_object_name = "movimentacoes"
       
# 🔹 CREATE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = MovimentacaoEstoqueForm()
        return render(request, "estoque/form_movimentacao.html", {"form": form})

    def post(self, request):
        form = MovimentacaoEstoqueForm(request.POST)

        if form.is_valid():
            try:
                form.save()  # 🔥 model resolve tudo
                return redirect("estoque:movimentacao_lista")

            except ValidationError as e:
                form.add_error(None, e)

        return render(request, "estoque/form_movimentacao.html", {"form": form})   

# 🔹 UPDATE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk):
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        form = MovimentacaoEstoqueForm(instance=movimentacao)
        form.fields['tipo'].disabled = True
        return render(request, "estoque/form_movimentacao.html", {
            "form": form,
            "movimentacao": movimentacao
        })

    def post(self, request, pk):
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        form = MovimentacaoEstoqueForm(request.POST, instance=movimentacao)

        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()  # 🔥 TODA lógica está no model

                return redirect("estoque:movimentacao_lista")

            except ValidationError as e:
                form.add_error(None, e)

        return render(request, "estoque/form_movimentacao.html", {
            "form": form,
            "movimentacao": movimentacao
        })       

# 🔹 DELETE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):  # ⚠️ não recomendado
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        movimentacao.delete()  # 🔥 model já reverte estoque
        return redirect("estoque:movimentacao_lista")   
    
    def post(self, request, pk):
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        movimentacao.delete()  # 🔥 model já reverte estoque

        return redirect("estoque:movimentacao_lista")
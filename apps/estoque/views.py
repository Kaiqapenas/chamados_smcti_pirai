from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.db.models import Max, ProtectedError
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib import messages

from .models import ItemEstoque, CategoriaItem, ItemImagem, MovimentacaoEstoque
from .forms import ItemEstoqueForm, CategoriaItemForm, MovimentacaoEstoqueForm

# 🔹 LISTVIEW ESTOQUE
class EstoqueListView(ListView):
    model = ItemEstoque
    template_name = "estoque/lista.html"
    context_object_name = "estoques"

    def get_queryset(self):
        qs = super().get_queryset()
        nome = self.request.GET.get("nome")
        categoria = self.request.GET.get("categoria")
        if nome:
            qs = qs.filter(nome__icontains=nome)
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        return qs

# 🔹 CREATE ESTOQUE
class EstoqueCreateView(View):
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
            messages.success(request, "Item criado com sucesso.")
            return redirect("estoque:editar", pk=item.id)
        return render(request, "estoque/form.html", {"form": form})

# 🔹 UPDATE ESTOQUE
class EstoqueUpdateView(View):
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
            messages.success(request, "Item atualizado com sucesso.")
            return redirect("estoque:editar", pk=item.id)

        return render(request, "estoque/form.html", {"form": form, "item": item})

# 🔹 DELETE ESTOQUE
class EstoqueDeleteView(View):

    def get(self, request, pk):
        item = get_object_or_404(ItemEstoque, pk=pk)
        return render(request, "estoque/confirm_delete.html", {"item": item})
    
    def post(self, request, pk):                          
        item = get_object_or_404(ItemEstoque, pk=pk)
        item.delete()
        messages.success(request, "Item excluído com sucesso.")
        return redirect("estoque:lista")
    
# 🔹 LISTVIEW CATEGORIA
class CategoriaEstoqueListView(ListView):
    model = CategoriaItem
    template_name = "estoque/lista_categoria.html"
    context_object_name = "categorias"
    
# 🔹 CREATE CATEGORIA
class CategoriaEstoqueCreateView(View):
    def get(self, request):
        form = CategoriaItemForm()
        return render(request, "estoque/form_categoria.html", {"form": form})

    def post(self, request):
        form = CategoriaItemForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Categoria criada com sucesso.")
            return redirect("estoque:categoria_lista")
    

        return render(request, "estoque/form_categoria.html", {"form": form})

# 🔹 UPDATE CATEGORIA
class CategoriaEstoqueUpdateView(View):
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
            messages.success(request, "Categoria atualizada com sucesso.")
            return redirect("estoque:categoria_lista")

        return render(request, "estoque/form_categoria.html", {
            "form": form,
            "categoria": categoria
        })

# 🔹 DELETE CATEGORIA
class CategoriaEstoqueDeleteView(View):
    def get(self, request, pk):  
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        return render(request, "estoque/confirm_delete_categoria.html", {"categoria": categoria})

    def post(self, request, pk):
        categoria = get_object_or_404(CategoriaItem, pk=pk)
        try:
            categoria.delete()
            messages.success(request, "Categoria excluída com sucesso.")
        except ProtectedError:
            messages.error(request, "Não é possível excluir esta categoria, existem itens associados a ela.")
        return redirect("estoque:categoria_lista")
 
# 🔹 LISTVIEW MOVIMENTAÇÃO ESTOQUE
class MovimentacaoEstoqueListView(ListView):
    model = MovimentacaoEstoque
    template_name = "estoque/lista_movimentacao.html"
    context_object_name = "movimentacoes"

    def get_queryset(self):
        qs = super().get_queryset()
        item_id = self.request.GET.get("item")
        tipo = self.request.GET.get("tipo")
        data_inicio = self.request.GET.get("data_inicio")
        data_fim = self.request.GET.get("data_fim")
        if item_id:
            qs = qs.filter(item_id=item_id)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if data_inicio:
            qs = qs.filter(data_movimentacao__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data_movimentacao__lte=data_fim)
        return qs
       
# 🔹 CREATE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueCreateView(View):

    def get(self, request):
        form = MovimentacaoEstoqueForm()
        return render(request, "estoque/form_movimentacao.html", {"form": form})

    def post(self, request):
        form = MovimentacaoEstoqueForm(request.POST)

        if form.is_valid():
            try:
                form.save()  # 🔥 model resolve tudo
                messages.success(request, "Movimentação criada com sucesso.")
                return redirect("estoque:movimentacao_lista")

            except ValidationError as e:
                form.add_error(None, e)

        return render(request, "estoque/form_movimentacao.html", {"form": form})   

# 🔹 UPDATE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueUpdateView(View):

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
                form.save()
                messages.success(request, "Movimentação atualizada com sucesso.")
                return redirect("estoque:movimentacao_lista")

            except ValidationError as e:
                form.add_error(None, e)

        return render(request, "estoque/form_movimentacao.html", {
            "form": form,
            "movimentacao": movimentacao
        })       

# 🔹 DELETE MOVIMENTACAO ESTOQUE
class MovimentacaoEstoqueDeleteView(View):
    def get(self, request, pk):
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        return render(request, "estoque/confirm_delete_movimentacao.html", {"movimentacao": movimentacao})
    
    def post(self, request, pk):
        movimentacao = get_object_or_404(MovimentacaoEstoque, pk=pk)
        try:
            movimentacao.delete()
            messages.success(request, "Movimentação excluída com sucesso.")
        except ValidationError as e:
            messages.error(request, str(e.message))
        return redirect("estoque:movimentacao_lista")
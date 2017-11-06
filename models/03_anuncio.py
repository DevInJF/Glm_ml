# -*- coding: utf-8 -*-

notempty=IS_NOT_EMPTY(error_message='Campo Obrigatório')
TIPOANUNCIO = {'gold_pro':'Premium','gold_special':'Clássico'}
CONDICAO = {'new':'Novo','used':'Usado'}

Categorias = db.define_table('categorias',
    Field('categoria','string',label='Categoria:',length=100),
    Field('categoria_id','string',label='Id Categoria',length=30),
    format = '%(categoria)s'
    )
Categorias.categoria.requires  = notempty
Categorias.categoria_id.requires = notempty

Anuncios = db.define_table('anuncios',
    Field('familia', 'reference familias'),
    Field('titulo', 'string', label='Título:', length=60),
    Field('item_id', 'string', label='ID do /Anuncio:', length=30),
    Field('categoria', 'string',label='Categoria:', length=30),
    Field('preco','decimal(7,2)',label='Preço'),
    Field('estoque','decimal(7,2)',label='Estoque'),
    Field('moeda','string', label='Moeda:', length=3),
    Field('modo','string',label='Mode de Compra:',length=30),
    Field('tipo','string',label='Tipo de Anuncio:', length=30),
    Field('condicao','string',label='Condição:',length=30),
    Field('garantia','string',label='Garantia',length=30),
    Field('descricao','reference descricoes', label='Descrição:')
    )
Anuncios.titulo.requires = notempty
Anuncios.moeda.default = 'BRL'
Anuncios.modo.default = 'buy_it_now'
Anuncios.garantia.default = 'None'
Anuncios.preco.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Anuncios.estoque.requires = IS_EMPTY_OR(IS_DECIMAL_IN_RANGE(dot=','))
Anuncios.tipo.requires = IS_IN_SET(TIPOANUNCIO,zero=None)
Anuncios.tipo.default = 'gold_pro'
Anuncios.condicao.requires = IS_IN_SET(CONDICAO,zero=None)
Anuncios.categoria.requires = IS_IN_DB(db,"categorias.categoria_id",'%(categoria)s',zero=None)

Anuncios_Produtos = db.define_table('anuncios_produtos',
    Field('anuncio', 'reference anuncios'),
    Field('produto', 'reference produtos'),
    )

Anuncios_Imagens = db.define_table('anuncios_imagens',
    Field('anuncio', 'reference anuncios'),
    Field('imagem','reference imagens'),
    )




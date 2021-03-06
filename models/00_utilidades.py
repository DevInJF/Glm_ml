def voltar(url):
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",_href=URL(url))

def voltar1(target):
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="jQuery(%s).get(0).reload()" %(target))
def voltar2():
    return A(SPAN(_class="glyphicon glyphicon-arrow-left"), ' Voltar ', _class="btn btn-warning",
                 _onClick="history.back()")
def excluir(url):
    return A(SPAN(_class="glyphicon glyphicon-trash"), ' Excluir ', _class="btn btn-danger", _href=url)
def novo(url):
    return A(SPAN(_class="glyphicon glyphicon-plus"), ' Novo ', _class="btn btn-info",_href=URL(url))
def proximo(url,id):
    return A(' Proximo ', SPAN(_class="glyphicon glyphicon-chevron-right"),  _class="btn btn-info",_href=URL(url,args=id))    
def anterior(url,id):
    return A(SPAN(_class="glyphicon glyphicon-chevron-left"), ' Anterior ', _class="btn btn-info",_href=URL(url,args=id))    
def pesquisar(controle,funcao,titulo):
    return A(SPAN(_class="btn btn-default glyphicon glyphicon-search"),'',_type="button",_id='pesquisar',
    _onclick="show_modal('%s','%s');" %(URL(controle,funcao,vars={'reload_div':'map'}),titulo))
def email(idcompra):
    return A(SPAN(_class="glyphicon glyphicon-file"),' Email',_class="btn btn-info",_id='email',
    _onclick="show_modal('%s','%s');" %(URL('pagar','enviarEmail',vars=dict(reload_div='map',id_compra=idcompra)),'Enviar Email de Pedido de Compra'))
def pdf(url,idpagar):
    return A(SPAN(_class="glyphicon glyphicon-file"), ' PDF ', _class="btn btn-info",_href=URL(url,vars=dict(id_pagar=idpagar)),_target = "_blank" )
def adicionar(controle,funcao,titulo):
    return A(SPAN(_class="glyphicon glyphicon-plus"),titulo,_class="btn btn-default",_id='adcionar',
    _onclick="show_modal('%s','%s');" %(URL(controle,funcao,vars={'reload_div':'map'}),titulo))
def atualizar(funcao,titulo,target):
    return A(SPAN(_class="glyphicon glyphicon-refresh"),titulo,_class="btn btn-default",_id='adcionar',
    _href='#', _onclick="ajax('%s',[],'%s');" % (URL(funcao, args=request.args(0)),target))

def publicar(funcao,titulo,target):
    return A(SPAN(_class="glyphicon glyphicon-cloud-upload"),titulo,_class="btn btn-success",_id='publicar',
    _href='#', _onclick="ajax('%s',[],'%s');" % (URL(funcao),target))

def grid(query,maxtextlength=50,paginate=100,**kwargs):
    
    grid = SQLFORM.grid(query,
                        user_signature=False,
                        showbuttontext=False,
                        csv=None,
                        maxtextlength=maxtextlength,
                        details=False,
                        paginate=paginate,
                        **kwargs)
    try:
        grid.element('.web2py_grid .web2py_table .web2py_htmltable')['_style'] = 'overflow: scroll; height:300px;'
    except Exception as e:
        pass   
    
    return grid

def lista_arquivos_imagem(caminho):
    """
    Retorna lista de arquivos de imagens encontrados no caminho espeficicado
    :param caminho: caminho para procurar imagens
    :return: lista de arquivos
    """
    import os
    arquivos = os.listdir(caminho)
    arquivos_tmp = []
    for file_name in arquivos:
            arquivos_tmp.append(file_name)

    image_extensions = ['bmp', 'pbm', 'pgm', 'ppm', 'sr', 'ras', 'jpeg', 'jpg', 'jpe', 'jp2', 'tiff', 'tif', 'png']
    # filtar somente os arquivos que contenham as extensões de imagens compatíves com opencv
    arquivos = ['%s%s.%s' % f for f in arquivos_tmp if f[2] in image_extensions]
    return arquivos

def sugerido(anuncio,idProduto = 0):

    idAnuncio = anuncio.id
    desconto = anuncio.desconto or 0
    
    preco = estoque = 0

    if idProduto == 0:

        q = (Produtos.id == Anuncios_Produtos.produto) & (Anuncios_Produtos.anuncio==idAnuncio)
        if anuncio.forma == 'Individual':
            max = Produtos.estoque.max()
            estoque = db(q).select(max).first()[max] or 0
            max = Produtos.preco.max()
            preco = db(q).select(max).first()[max] or 0
        elif anuncio.forma =='Multiplos':
            sum = Produtos.estoque.sum()
            estoque = db(q).select(sum).first()[sum] or 0
            max = Produtos.preco.max() 
            preco = db(q).select(max).first()[max] or 0
        elif anuncio.forma =='Kit':
            min = Produtos.estoque.min()
            estoque = db(q).select(min).first()[min] or 0
            sum = Produtos.preco.sum() 
            preco = db(q).select(sum).first()[sum]  or 0

    else:
        preco = Produtos[idProduto].preco

    empresa = db(Empresa.id==1).select().first()

    if anuncio.tipo == 'gold_pro':
        tarifa = empresa.premium
    elif anuncio.tipo == 'gold_special':
        tarifa = empresa.classico

    categoria = db(Categorias.categoria_id == anuncio.categoria).select().first()
    
    if anuncio.frete == 'gratis':
        frete = int(categoria.frete) * (1 - empresa.desconto/100)
        frete2 = 0
    else:
        frete = 0
        frete2 = 5
    
    preco = preco * (1 - desconto/100)
    preco = preco + frete + frete2
    preco = preco/ (1-tarifa/100)
    preco = round(preco,1)

    if preco >= (120-frete2) and preco < 126:
        preco = 119.90

    if idProduto == 0:
        return dict(estoque=estoque,preco=preco)
    else:
        return preco

def buscar_categoria(categoriaId):
    import json
    from meli import Meli
    meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
    ### Buscar Categoria ###
    args = "categories/%s" %(categoriaId)
    categoria = meli.get(args) 
    if categoria.status_code == 200:
        categoria = json.loads(categoria.content) 
    
    ### Concatena Nome da Categoria ###
    nomeCategoria = ''
    for r in categoria['path_from_root']:
        if nomeCategoria:
            nomeCategoria = nomeCategoria + '/' + r['name']
        else:
            nomeCategoria = r['name']

    ### Buscar Dimensoes por Categoria ###
    valorFrete = 0
    argsDimensoes = '%s/shipping' %(args)
    categoriaDimensoes = meli.get(argsDimensoes)
    if categoriaDimensoes.status_code == 200:
        dimensoes = json.loads(categoriaDimensoes.content) 
       
        ### Buscar Valor de Frete pelas Dimensoes da Categoria ###
        argsFrete = '/users/%s/shipping_options/free?dimensions=%sx%sx%s,%s' \
        %(USER_ID,dimensoes['height'],dimensoes['width'],dimensoes['length'],dimensoes['weight'])
        categoriaFrete = categoria = meli.get(argsFrete) 

        if categoriaFrete.status_code == 200:
            frete = json.loads(categoriaFrete.content)
            valorFrete = frete['coverage']['all_country']['list_cost']

    return dict(categoria = nomeCategoria, categoriaId=categoriaId,valorFrete=valorFrete)
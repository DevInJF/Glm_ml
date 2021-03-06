def importar_vendas():
	import json
	from datetime import datetime

	form = SQLFORM.factory(
		Field('order_id','string',label='Id do Pedido:'),
		Field('offset','integer',label='Inicio:', default=0),
		Field('limit','integer',label='Quantidade:',default=50,requires=IS_INT_IN_RANGE(1, 51,error_message='Entre 1 e 50 !')),
		table_name='importarvendas',
		submit_button='Importar Pedidos',
		)

	itens = []

	if form.process().accepted:

		order_id = form.vars.order_id
		offset = form.vars.offset
		limit = form.vars.limit 

		if session.ACCESS_TOKEN:
			from meli import Meli 
			meli = Meli(client_id=CLIENT_ID,client_secret=CLIENT_SECRET, access_token=session.ACCESS_TOKEN, refresh_token=session.REFRESH_TOKEN)

			if order_id:
				args = "orders/%s" %(order_id)
				busca = meli.get(args,{'access_token':session.ACCESS_TOKEN})
				if busca.status_code == 200:
					xitens = json.loads(busca.content)    
					itens.append(xitens)
			else:
				args = "/orders/search/recent?seller=%s&sort=date_desc&order.status=paid&offset=%s&limit=%s" %(USER_ID,offset,limit)
				busca = meli.get(args,{'access_token':session.ACCESS_TOKEN})
				#busca = meli.get("/orders/search/recent?seller=158428813&sort=date_desc&order.status=paid", {'access_token':session.ACCESS_TOKEN})
			
				if busca.status_code == 200:
					itens = json.loads(busca.content)    
					itens = itens['results']

		for item in itens:

			body = "/shipments/%s" %(item['shipping']['id'])
			busca = meli.get(body, {'access_token':session.ACCESS_TOKEN})

			if busca.status_code == 200:
				shipping = json.loads(busca.content)
				
				Clientes.update_or_insert(Clientes.id == item['buyer']['id'],
	                id = item['buyer']['id'],
	                nome = "%s %s" %(item['buyer']['first_name'],item['buyer']['last_name']),
	                cnpj_cpf = item['buyer']['billing_info']['doc_number'],
	                tipo = item['buyer']['billing_info']['doc_type'],
	                endereco = shipping['destination']['shipping_address']['address_line'], 
	                bairro = shipping['destination']['shipping_address']['neighborhood']['name'],
	                cidade = shipping['destination']['shipping_address']['city']['name'],
	                estado = shipping['destination']['shipping_address']['state']['name'],
	                cep = shipping['destination']['shipping_address']['zip_code'],
	                fone = "%s %s" %(item['buyer']['phone']['area_code'] or '',item['buyer']['phone']['number'] or ''),
	                email = item['buyer']['email'],
	                apelido = item['buyer']['nickname'],
	                )
				
				
				Pedidos.update_or_insert(Pedidos.id == item['shipping']['id'],
					id = item['shipping']['id'],
					buyer_id = item['buyer']['id'],
					date_created = datetime.strptime(item['date_created'][:10],'%Y-%m-%d'),
					status = shipping['status']
					)

				Pedidos_Itens.update_or_insert(Pedidos_Itens.id == item['id'],
					id = item['id'],
					shipping_id = item['shipping']['id'],
					payments_id = item['payments'][0]['id'],
					item = item['order_items'][0]['item']['title'],
					item_id = item['order_items'][0]['item']['id'],
					quantidade =  item['order_items'][0]['quantity'],
					valor = item['order_items'][0]['unit_price'],
					taxa = 0,
					frete = 0, 
					)

		else:
			status = 'Antes Faça o Login....'

	elif form.errors:
	    response.flash = 'Erro no Formulário'

	return dict(itens=itens,form=form)

def exportar(ids):
	print ids

def exportar_vendas():
	fields = (Pedidos.date_created,Pedidos.id,Pedidos.buyer_id,Pedidos.valor,Pedidos.status)
	selectable = lambda ids: exportar(ids)
	gridPedidos = grid(Pedidos,create=False, editable=False,deletable=False,formname="pedidos",
		fields=fields,orderby =~ Pedidos.date_created,selectable=selectable,selectable_submit_button='Exportar Pedidos',)
        
	gridPedidos = DIV(gridPedidos, _class="well")

	return dict(gridPedidos=gridPedidos)
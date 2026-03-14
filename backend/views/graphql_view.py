"""
GraphQL view для Pyramid приложения.
"""

import json
from pyramid.view import view_config
from pyramid.response import Response
from backend.schemas.simple_schema import schema


@view_config(route_name='graphql', request_method='POST', renderer='json')
def graphql_view(request):
    """
    Обработчик GraphQL запросов.
    
    Поддерживает:
    - Стандартный GraphQL POST запрос
    - Переменные GraphQL
    - Операционные имена
    - CORS (уже настроено в backend/__init__.py)
    """
    try:
        # Получаем данные запроса
        content_type = request.content_type or ''
        
        if 'application/json' in content_type:
            # JSON запрос
            data = request.json_body
            query = data.get('query')
            variables = data.get('variables')
            operation_name = data.get('operationName')
        elif 'application/graphql' in content_type:
            # Raw GraphQL запрос
            query = request.body.decode('utf-8')
            variables = None
            operation_name = None
        else:
            # Форма или другие форматы
            query = request.params.get('query')
            variables_str = request.params.get('variables')
            operation_name = request.params.get('operationName')
            
            # Парсим переменные если они есть
            variables = json.loads(variables_str) if variables_str else None
        
        # Проверяем наличие запроса
        if not query:
            return Response(
                json.dumps({
                    'errors': [{
                        'message': 'No GraphQL query provided',
                        'extensions': {'code': 'NO_QUERY'}
                    }]
                }),
                status=400,
                content_type='application/json'
            )
        
        # Контекст для GraphQL
        context = {
            'request': request,
            'session': request.dbsession if hasattr(request, 'dbsession') else None
        }
        
        # Выполняем GraphQL запрос через Graphene schema
        result = schema.execute(
            query,
            variables=variables,
            operation_name=operation_name,
            context=context
        )
        
        # Формируем ответ
        response_data = {}
        
        if result.data:
            response_data['data'] = result.data
        
        if result.errors:
            response_data['errors'] = [
                {
                    'message': error.message,
                    'locations': [
                        {'line': loc.line, 'column': loc.column}
                        for loc in (error.locations or [])
                    ],
                    'path': error.path,
                    'extensions': getattr(error, 'extensions', None)
                }
                for error in result.errors
            ]
        
        # Возвращаем ответ
        return Response(
            json.dumps(response_data, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=200 if not result.errors else 400
        )
    
    except json.JSONDecodeError as e:
        # Ошибка парсинга JSON
        return Response(
            json.dumps({
                'errors': [{
                    'message': f'Invalid JSON: {str(e)}',
                    'extensions': {'code': 'INVALID_JSON'}
                }]
            }),
            status=400,
            content_type='application/json'
        )
    
    except Exception as e:
        # Неожиданная ошибка
        import traceback
        traceback.print_exc()
        
        return Response(
            json.dumps({
                'errors': [{
                    'message': f'Internal server error: {str(e)}',
                    'extensions': {'code': 'INTERNAL_ERROR'}
                }]
            }),
            status=500,
            content_type='application/json'
        )


@view_config(route_name='graphql', request_method='GET', renderer='json')
def graphql_playground(request):
    """
    Endpoint для GraphQL Playground или простой информации.
    
    В production можно отключить или защитить.
    """
    # Проверяем, запрашивают ли GraphiQL/Playground
    accept = request.headers.get('Accept', '')
    
    if 'text/html' in accept:
        # Возвращаем HTML для GraphiQL/Playground
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CRM GraphQL API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                pre { background: #f5f5f5; padding: 10px; border-radius: 5px; }
                code { color: #d63384; }
            </style>
        </head>
        <body>
            <h1>CRM GraphQL API</h1>
            <p>GraphQL endpoint is available at <code>/graphql</code></p>
            <p>Use POST requests with JSON body:</p>
            <pre>
{
  "query": "query { hello }",
  "variables": {}
}
            </pre>
            <p>Available queries:</p>
            <ul>
                <li><code>hello</code> - Test query</li>
                <li><code>version</code> - API version</li>
                <li><code>contact(id: ID!)</code> - Get contact by ID</li>
                <li><code>contacts(page: Int, per_page: Int, filter: ContactFilter)</code> - List contacts</li>
                <li><code>search_contacts(query: String!, limit: Int)</code> - Search contacts</li>
            </ul>
            <p>Available mutations:</p>
            <ul>
                <li><code>create_contact(input: ContactInput!)</code> - Create contact</li>
                <li><code>update_contact(id: ID!, input: ContactInput!)</code> - Update contact</li>
                <li><code>delete_contact(id: ID!)</code> - Delete contact</li>
                <li><code>create_contact_detailed(input: ContactInput!)</code> - Create with detailed output</li>
                <li><code>update_contact_detailed(id: ID!, input: ContactInput!)</code> - Update with detailed output</li>
            </ul>
            <p>For GraphiQL or Playground, install a GraphQL client or use curl:</p>
            <pre>
curl -X POST http://localhost:6543/graphql \\
  -H "Content-Type: application/json" \\
  -d '{"query": "query { hello }"}'
            </pre>
        </body>
        </html>
        """
        
        return Response(
            html,
            content_type='text/html'
        )
    
    # Возвращаем JSON информацию
    return {
        'graphql': True,
        'endpoint': '/graphql',
        'methods': ['GET', 'POST'],
        'description': 'GraphQL API for CRM system',
        'version': '1.0.0',
        'examples': {
            'simple_query': {
                'query': 'query { hello }'
            },
            'get_contact': {
                'query': 'query($id: ID!) { contact(id: $id) { id full_name company } }',
                'variables': {'id': '1'}
            },
            'create_contact': {
                'query': '''
                mutation($input: ContactInput!) {
                  create_contact(input: $input) {
                    id full_name company
                  }
                }
                ''',
                'variables': {
                    'input': {
                        'full_name': 'John Doe',
                        'company': 'Example Corp'
                    }
                }
            }
        }
    }


@view_config(route_name='graphql', request_method='OPTIONS', renderer='json')
def graphql_options(request):
    """
    Обработчик OPTIONS запросов для CORS.
    """
    # CORS уже настроен в backend/__init__.py через add_cors_headers
    return Response(status=200)
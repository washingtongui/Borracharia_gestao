from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from gestaoClientes.views import listar_clientes


class FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def execute(self, *args, **kwargs):
        return self

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, rows):
        self._rows = rows

    def cursor(self):
        return FakeCursor(self._rows)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class ListarClientesViewTests(SimpleTestCase):
    def test_view_renders_data_when_query_succeeds(self):
        request = RequestFactory().get('/listar/')
        rows = [(1, 'Ana Silva', '123', '99999', 'ana@example.com', None)]

        with patch('busca_cliente.views.pyodbc.connect', return_value=FakeConnection(rows)):
            response = listar_clientes(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ana Silva')

    def test_view_renders_when_query_fails(self):
        request = RequestFactory().get('/listar/')

        with patch('busca_cliente.views.pyodbc.connect', side_effect=Exception('permission denied')):
            response = listar_clientes(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Não foi possível consultar os clientes')

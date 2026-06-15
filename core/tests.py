<<<<<<< Updated upstream
from django.test import TestCase, Client, SimpleTestCase
from unittest.mock import patch, MagicMock
from .models import HardwareComponent, BenchmarkSession, Hardware, User
from .services import calculate_session_metrics, toggle_overlay_state, calculate_performance_gap
import json
import uuid




# =============================================================================
# RF_11 – GESTIONAR COMPONENTES DEL RANKING GLOBAL
# =============================================================================

class HardwareComponentTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_header = {'HTTP_X_USER_ADMIN': 'true'}
        self.component_data = {
            'brand': 'NVIDIA',
            'model': 'RTX 4090',
            'type': 'GPU',
            'launch_year': 2022,
            'base_score': 36820.0,
        }

    def _MockComponent(self):
        """Crea un componente falso con los valores del setUp."""
        mock_component = MagicMock(spec=HardwareComponent)
        mock_component.id = uuid.uuid4()
        mock_component.brand = 'NVIDIA'
        mock_component.model = 'RTX 4090'
        mock_component.type = 'GPU'
        mock_component.base_specs = ''
        mock_component.launch_year = 2022
        mock_component.base_score = 36820.0
        mock_component.created_at.isoformat.return_value = '2024-05-24T00:00:00Z'
        mock_component.updated_at.isoformat.return_value = '2024-05-24T00:00:00Z'
        return mock_component

    @patch('core.views.HardwareComponent.objects.create')
    def test_CreateComponentAsAdmin(self, mock_create):
        """Happy path: admin crea un componente correctamente."""
        mock_create.return_value = self._MockComponent()
        response = self.client.post(
            '/components/',
            data=json.dumps(self.component_data),
            content_type='application/json',
            **self.admin_header,
        )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_once()

    def test_CreateComponentForbiddenWithoutAdmin(self):
        """Error: usuario sin permisos de admin no puede crear componentes."""
        response = self.client.post(
            '/components/',
            data=json.dumps(self.component_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    @patch('core.views.get_object_or_404')
    def test_DeleteComponentAsAdmin(self, mock_get):
        """Edge case: admin elimina un componente correctamente."""
        mock_component = self._MockComponent()
        mock_get.return_value = mock_component
        response = self.client.delete(
            f'/components/{mock_component.id}/',
            content_type='application/json',
            **self.admin_header,
        )
        self.assertEqual(response.status_code, 200)
        mock_component.delete.assert_called_once()


# =============================================================================
# RF_9 – ALMACENAR RESULTADOS ANÓNIMOS PARA RANKING GLOBAL
# =============================================================================

class TelemetrySubmitTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_payload = {
            'started_at': '2024-05-24T00:00:00Z',
            'ended_at': '2024-05-24T00:14:22Z',
            'cpu_avg': 68.0,
            'cpu_max': 98.4,
            'gpu_avg': 82.0,
            'gpu_max': 100.0,
            'ram_avg_gb': 24.0,
            'ram_max_gb': 42.0,
            'score': 12840.0,
        }

    def _MockSession(self):
        """Crea una sesión falsa con los valores del setUp."""
        mock_session = MagicMock(spec=BenchmarkSession)
        mock_session.id = uuid.uuid4()
        mock_session.is_anonymous = True
        mock_session.hardware = None
        mock_session.score = 12840.0
        return mock_session

    @patch('core.views._recalculate_ranking')
    @patch('core.views.BenchmarkSession.objects.create')
    def test_SubmitTelemetryCreatesSession(self, mock_create, mock_recalculate):
        """Happy path: paquete válido crea una BenchmarkSession anónima."""
        mock_create.return_value = self._MockSession()
        response = self.client.post(
            '/telemetry/',
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_once()
        mock_recalculate.assert_called_once()

    def test_SubmitTelemetryMissingFieldsReturns400(self):
        """Error: paquete con campos obligatorios faltantes es rechazado."""
        incomplete_payload = {'started_at': '2024-05-24T00:00:00Z'}
        response = self.client.post(
            '/telemetry/',
            data=json.dumps(incomplete_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400)
        body = json.loads(response.content)
        self.assertIn('Missing fields', body['error'])

    @patch('core.views._recalculate_ranking')
    @patch('core.views.BenchmarkSession.objects.create')
    def test_SubmitTelemetryCallsRecalculate(self, mock_create, mock_recalculate):
        """Edge case: después de guardar la sesión se ejecuta el recálculo del ranking."""
        mock_session = self._MockSession()
        mock_create.return_value = mock_session
        self.client.post(
            '/telemetry/',
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )
        mock_recalculate.assert_called_once_with(mock_session)


# =============================================================================
# RF_13 – GENERAR INFORME TÉCNICO DETALLADO DE SESIÓN
# =============================================================================

class SessionReportTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.fake_id = uuid.uuid4()

    def _MockSession(self):
        """Crea una sesión falsa con métricas completas."""
        mock_session = MagicMock(spec=BenchmarkSession)
        mock_session.id = self.fake_id
        mock_session.score = 12840.0
        mock_session.is_anonymous = False
        mock_session.hardware = None
        mock_session.cpu_avg = 68.0
        mock_session.cpu_max = 98.4
        mock_session.cpu_temp_avg = 74.0
        mock_session.cpu_temp_max = 80.0
        mock_session.gpu_avg = 82.0
        mock_session.gpu_max = 100.0
        mock_session.gpu_temp_avg = 65.0
        mock_session.gpu_temp_max = 82.0
        mock_session.ram_avg_gb = 24.0
        mock_session.ram_max_gb = 42.0
        mock_session.disk_read_avg = 450.0
        mock_session.disk_write_avg = 1100.0
        mock_session.started_at.isoformat.return_value = '2024-05-24T00:00:00Z'
        mock_session.ended_at.isoformat.return_value = '2024-05-24T00:14:22Z'
        mock_session.created_at.isoformat.return_value = '2024-05-24T00:14:22Z'
        mock_session.ended_at.__sub__ = lambda self, other: MagicMock(total_seconds=lambda: 862)
        mock_session.samples.values.return_value = []
        return mock_session

    @patch('core.views.get_object_or_404')
    def test_ReportReturnsCorrectStructure(self, mock_get):
        """Happy path: el informe contiene todas las secciones requeridas."""
        mock_get.return_value = self._MockSession()
        response = self.client.get(f'/sessions/{self.fake_id}/report/')
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertIn('metrics', body)
        self.assertIn('timeline', body)
        self.assertIn('peak_events', body)
        self.assertIn('hardware', body)

    @patch('core.views.get_object_or_404')
    def test_ReportNonexistentSessionReturns404(self, mock_get):
        """Error: solicitar informe de sesión inexistente retorna 404."""
        from django.http import Http404
        mock_get.side_effect = Http404
        fake_id = uuid.uuid4()
        response = self.client.get(f'/sessions/{fake_id}/report/')
        self.assertEqual(response.status_code, 404)

    @patch('core.views.BenchmarkSession.objects.order_by')
    def test_SessionListReturnsAllSessions(self, mock_order_by):
        """Edge case: el historial lista todas las sesiones registradas."""
        mock_session_1 = MagicMock()
        mock_session_1.id = uuid.uuid4()
        mock_session_1.score = 12840.0
        mock_session_1.is_anonymous = False
        mock_session_1.started_at.isoformat.return_value = '2024-05-24T00:00:00Z'
        mock_session_1.ended_at.isoformat.return_value = '2024-05-24T00:14:22Z'
        mock_session_1.created_at.isoformat.return_value = '2024-05-24T00:14:22Z'

        mock_session_2 = MagicMock()
        mock_session_2.id = uuid.uuid4()
        mock_session_2.score = 9500.0
        mock_session_2.is_anonymous = True
        mock_session_2.started_at.isoformat.return_value = '2024-05-25T00:00:00Z'
        mock_session_2.ended_at.isoformat.return_value = '2024-05-25T00:10:00Z'
        mock_session_2.created_at.isoformat.return_value = '2024-05-25T00:10:00Z'

        mock_order_by.return_value = [mock_session_1, mock_session_2]

        response = self.client.get('/sessions/')
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(len(body), 2)=======

# =============================================================================
# CU_01 – RESUMEN TÉCNICO DE FPS
# =============================================================================
class SessionMetricsTests(SimpleTestCase):

    def test_CalculateMetricsNormal(self):
        """Happy path: cálculo correcto de métricas con datos válidos."""
        fps_data = [60, 144, 30, 80, 120]
        result = calculate_session_metrics(fps_data)
        self.assertEqual(result['max_fps'], 144)
        self.assertEqual(result['min_fps'], 30)
        self.assertEqual(result['avg_fps'], 86.8)

    def test_CalculateMetricsEmpty(self):
        """Edge case: el juego se cierra sin recolectar FPS."""
        result = calculate_session_metrics([])
        self.assertEqual(result['max_fps'], 0)
        self.assertEqual(result['avg_fps'], 0.0)


# =============================================================================
# CU_02 – MOSTRAR INTERFAZ SOBREPUESTA (TOGGLE)
# =============================================================================
class OverlayStateTests(SimpleTestCase):

    def test_ToggleStateSuccess(self):
        """Happy path: cambio de estado de visibilidad correctamente."""
        self.assertFalse(toggle_overlay_state(True))
        self.assertTrue(toggle_overlay_state(False))

    def test_ToggleStateInvalidInputReturnsError(self):
        """Error: recibe un tipo de dato que no es booleano."""
        with self.assertRaises(ValueError):
            toggle_overlay_state("Visible")


# =============================================================================
# CU_03 – COMPARATIVA CON MERCADO ESTÁNDAR
# =============================================================================
class MarketComparisonTests(SimpleTestCase):

    def test_PerformanceGapPositive(self):
        """Happy path: PC del usuario es mejor que el mercado estándar."""
        gap = calculate_performance_gap(120, 60)
        self.assertEqual(gap, 100.0)

    def test_PerformanceGapNegative(self):
        """Happy path: PC del usuario es peor que el mercado estándar."""
        gap = calculate_performance_gap(30, 60)
        self.assertEqual(gap, -50.0)

    def test_PerformanceGapZeroDivision(self):
        """Edge case: evitar crash si los datos del mercado están en cero."""
        gap = calculate_performance_gap(144, 0)
        self.assertEqual(gap, 0.0)
>>>>>>> Stashed changes

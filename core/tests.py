from django.test import TestCase, Client
from .models import HardwareComponent, BenchmarkSession, Hardware, User
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

    def test_CreateComponentAsAdmin(self):
        """Happy path: admin crea un componente correctamente."""
        response = self.client.post(
            '/components/',
            data=json.dumps(self.component_data),
            content_type='application/json',
            **self.admin_header,
        )
        self.assertEqual(response.status_code, 201)
        body = json.loads(response.content)
        self.assertEqual(body['model'], 'RTX 4090')

    def test_CreateComponentForbiddenWithoutAdmin(self):
        """Error: usuario sin permisos de admin no puede crear componentes."""
        response = self.client.post(
            '/components/',
            data=json.dumps(self.component_data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_DeleteComponentAsAdmin(self):
        """Edge case: admin elimina un componente y ya no aparece en el listado."""
        component = HardwareComponent.objects.create(**self.component_data)
        response = self.client.delete(
            f'/components/{component.id}/',
            content_type='application/json',
            **self.admin_header,
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(HardwareComponent.objects.filter(pk=component.id).exists())


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

    def test_SubmitTelemetryCreatesSession(self):
        """Happy path: paquete válido crea una BenchmarkSession anónima."""
        response = self.client.post(
            '/telemetry/',
            data=json.dumps(self.valid_payload),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(BenchmarkSession.objects.filter(is_anonymous=True).exists())

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

    def test_SubmitTelemetryUpdatesComponentScore(self):
        """Edge case: telemetría anónima recalcula el base_score del componente."""
        test_user = User.objects.create(
            username='testuser',
            email='test@test.com',
            password_hash='hash',
        )
        test_hardware = Hardware.objects.create(
            user=test_user,
            cpu='Core i9-14900K',
            gpu='RTX 4090',
            gb_ram=64,
            storage_type='NVMe',
        )
        HardwareComponent.objects.create(
            brand='NVIDIA',
            model='RTX 4090',
            type='GPU',
            base_score=0.0,
        )
        payload = {**self.valid_payload, 'hardware_id': str(test_hardware.id)}
        self.client.post(
            '/telemetry/',
            data=json.dumps(payload),
            content_type='application/json',
        )
        component = HardwareComponent.objects.get(model='RTX 4090', type='GPU')
        self.assertEqual(component.base_score, 12840.0)


# =============================================================================
# RF_13 – GENERAR INFORME TÉCNICO DETALLADO DE SESIÓN
# =============================================================================

class SessionReportTests(TestCase):

    def setUp(self):
        self.client = Client()
        test_user = User.objects.create(
            username='analista',
            email='analista@test.com',
            password_hash='hash',
        )
        test_hardware = Hardware.objects.create(
            user=test_user,
            cpu='Core i9-14900K',
            gpu='RTX 4090',
            gb_ram=64,
            storage_type='NVMe',
        )
        self.session = BenchmarkSession.objects.create(
            hardware=test_hardware,
            started_at='2024-05-24T00:00:00Z',
            ended_at='2024-05-24T00:14:22Z',
            cpu_avg=68.0,
            cpu_max=98.4,
            gpu_avg=82.0,
            gpu_max=100.0,
            ram_avg_gb=24.0,
            ram_max_gb=42.0,
            score=12840.0,
        )

    def test_ReportReturnsCorrectStructure(self):
        """Happy path: el informe contiene todas las secciones requeridas."""
        response = self.client.get(f'/sessions/{self.session.id}/report/')
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertIn('metrics', body)
        self.assertIn('timeline', body)
        self.assertIn('peak_events', body)
        self.assertIn('hardware', body)

    def test_ReportNonexistentSessionReturns404(self):
        """Error: solicitar informe de una sesión inexistente retorna 404."""
        fake_id = uuid.uuid4()
        response = self.client.get(f'/sessions/{fake_id}/report/')
        self.assertEqual(response.status_code, 404)

    def test_SessionListReturnsAllSessions(self):
        """Edge case: el historial lista todas las sesiones registradas."""
        test_user = User.objects.get(username='analista')
        test_hardware = Hardware.objects.get(user=test_user)
        BenchmarkSession.objects.create(
            hardware=test_hardware,
            started_at='2024-05-25T00:00:00Z',
            ended_at='2024-05-25T00:10:00Z',
            cpu_avg=50.0,
            cpu_max=75.0,
            gpu_avg=60.0,
            gpu_max=80.0,
            ram_avg_gb=16.0,
            ram_max_gb=20.0,
        )
        response = self.client.get('/sessions/')
        self.assertEqual(response.status_code, 200)
        body = json.loads(response.content)
        self.assertEqual(len(body), 2)
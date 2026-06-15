<<<<<<< Updated upstream
from django.test import TestCase

# Create your tests here.
=======
from django.test import TestCase, Client, SimpleTestCase
from .models import HardwareComponent, BenchmarkSession, Hardware, User
from .services import calculate_session_metrics, toggle_overlay_state, calculate_performance_gap
import json
import uuid

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

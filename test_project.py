import asyncio
import base64
import json
import unittest
from unittest.mock import AsyncMock, patch
from types import SimpleNamespace
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service
from backend.config import settings


class ProjectTests(unittest.TestCase):
    def test_design_score_bounds(self):
        from backend.models.schemas import ImageAnalysis
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ImageAnalysis(design_score=11,animation_potential='Идея анимации', evidence_limitations='Статичный снимок')

    def test_empty_json_is_not_success(self):
        response=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{}'))])
        async def check():
            with patch.object(settings,'proxy_api_key','test-key'), patch.object(
                openai_service.client.chat.completions,'create',AsyncMock(return_value=response)):
                with self.assertRaises(ValueError):
                    await openai_service.analyze_text('Публичный текст конкурента')
        asyncio.run(check())

    def test_parser_rejects_internal_url(self):
        result=asyncio.run(parser_service.parse_url('http://127.0.0.1/.env'))
        self.assertIsNotNone(result[-1])

    def test_capture_returns_actual_jpeg(self):
        result=asyncio.run(parser_service.parse_url('https://n8n.io/'))
        self.assertIsNone(result[-1])
        self.assertTrue(result[3].startswith(b'\xff\xd8\xff'))
        self.assertIn('n8n',result[0])

    def test_invalid_upload_does_not_call_model(self):
        with patch.object(openai_service,'analyze_image',AsyncMock()) as call:
            result=TestClient(app).post('/analyzeimage',files={'file':('fake.png',b'not-an-image','image/png')})
            self.assertFalse(result.json()['success'])
            call.assert_not_called()


if __name__=='__main__':
    unittest.main()

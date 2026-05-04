-- Pragma - Django OCR Invoice Processing System
-- Author: Pragma Team
-- Date: 2026-03-18
-- Description: Representative SQL mock dataset for demonstration

INSERT INTO core_cliente (id, nit, nombre, contacto, created_at, updated_at) VALUES
  (1, '1000001-1', 'Cliente Uno', 'cliente1@example.com', NOW(), NOW()),
  (2, '1000002-1', 'Cliente Dos', 'cliente2@example.com', NOW(), NOW())
ON CONFLICT (id) DO NOTHING;

INSERT INTO core_factura (
    id, numero_factura, monto, fecha, cliente_nit, archivo, ocr_data, created_at, updated_at, cliente_id
) VALUES
  (
    1, 'FAC-001-001', 751.00, '2026-03-02', '1000001-1',
    'facturas/factura_FAC-001-001.pdf',
    '{"numero_factura":"FAC-001-001","cliente_nit":"1000001-1","monto":"751.00","fecha":"2026-03-02","errors":[]}',
    NOW(), NOW(), 1
  ),
  (
    2, 'FAC-002-001', 752.00, '2026-03-02', '1000002-1',
    'facturas/factura_FAC-002-001.pdf',
    '{"numero_factura":"FAC-002-001","cliente_nit":"1000002-1","monto":"752.00","fecha":"2026-03-02","errors":[]}',
    NOW(), NOW(), 2
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO core_certificadobancario (
    id, numero_referencia, monto, fecha, cliente_nit, archivo, created_at, updated_at, cliente_id
) VALUES
  (1, 'REF-001-001', 751.00, '2026-03-02', '1000001-1', 'certificados/certificado_REF-001-001.pdf', NOW(), NOW(), 1),
  (2, 'REF-002-001', 777.00, '2026-03-02', '1000002-1', 'certificados/certificado_REF-002-001.pdf', NOW(), NOW(), 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO core_detallepago (
    id, estado_match, diferencias, resumen, created_at, updated_at, match_score, certificado_id, factura_id
) VALUES
  (
    1, 'match', '',
    'La factura y el certificado bancario coinciden completamente.',
    NOW(), NOW(), 100.00, 1, 1
  ),
  (
    2, 'partial',
    'monto: factura=752.00 | certificado=777.00. Los montos no coinciden.',
    'Se detectó coincidencia parcial (60.00%). Diferencias: monto: factura=752.00 | certificado=777.00. Los montos no coinciden.',
    NOW(), NOW(), 60.00, 2, 2
  )
ON CONFLICT (id) DO NOTHING;

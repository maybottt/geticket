INSERT INTO public.institucion
(nombre, descripcion, direccion, telefono, email, estado, created_at, updated_at)
VALUES
-- CENTROS DE SALUD (4)
('Hospital General del Sur', 'Centro hospitalario ', 'Av. Libertador 1234, Zona Sur', '+54 11 4321-0987', 'contacto@hospitaldelsur.com', 'activo', NOW(), NOW()),
('Clínica San Miguel', 'Atención médica privada', 'Calle Rivadavia 567, Centro', '+54 11 5678-1234', 'info@clinicasanmiguel.com', 'activo', NOW(), NOW()),
('Centro de Salud Santa Fe', 'Atención primaria', 'Belgrano 890, Barrio Norte', '+54 341 3456-789', 'salud@santafe.gob.ar', 'activo', NOW(), NOW()),
('Consultorios Médicos Integrales', 'Especialidades en traumatología', 'San Martín 234, Zona Oeste', '+54 261 2345-678', 'turnos@consultoriosintegrales.com', 'inactivo', NOW(), NOW()),

-- COLEGIOS (3)
('Colegio Santo Tomás', 'Educación primaria y secundaria', 'Av. Colón 4567, Palermo', '+54 11 7890-3456', 'secretaria@stotomas.edu.ar', 'activo', NOW(), NOW()),
('Instituto Privado Belgrano', 'Jardín, primaria y secundaria', 'Cabrera 890, Belgrano', '+54 11 9012-3456', 'admision@belgrano.edu.ar', 'activo', NOW(), NOW()),
('Escuela Técnica N° 10', 'Formación técnica en electrónica y sistemas', 'Av. Mitre 345, Villa Crespo', '+54 11 1234-7890', 'tecnica10@educacion.gob.ar', 'inactivo', NOW(), NOW()),

-- TIENDAS (3)
('Supermercado El Ahorro', 'Cadena de supermercadoS', 'Av. Corrientes 2345, Abasto', '+54 11 4567-8901', 'atencion@elahorro.com.ar', 'activo', NOW(), NOW()),
('Tienda de Barrio Don Pepe', 'Almacén', 'Rawson 678, Flores', '+54 11 6789-0123', 'donpepe@almacen.com.ar', 'activo', NOW(), NOW()),
('Electro Hogar', 'Venta de electrodomésticos para el hogar', 'Av. Santa Fe 3456, Recoleta', '+54 11 8901-2345', 'ventas@electrohogar.com', 'activo', NOW(), NOW());



INSERT INTO public.sistema
(nombre, "version", estado, created_at, updated_at, id_institucion)
VALUES('', '', '', NOW(), NOW(), 0);
NOMBRES: ERP-GeCOIN, HIS-GeHOMED, LIS-GeLIS, GeDOCTOR, SYSMAN pos, FACSIN 
VERSIONES: 15.20.01.51 y similares 
ESTADO: activo o innactivo o eliminado 

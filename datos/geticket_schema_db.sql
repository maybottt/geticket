-- ============================================================
-- GETICKET - Script de Base de Datos
-- Motor: PostgreSQL 17
-- Estilo: snake_case
-- Formato timestamp: YYYY-MM-DD HH:MM:SS
-- ============================================================

-- ============================================================
-- TABLA: USUARIO
-- ============================================================
CREATE TABLE usuario (
    id_usuario      SERIAL          PRIMARY KEY,
    email           VARCHAR(255)    NOT NULL UNIQUE,
    password        VARCHAR(255)    NOT NULL,
    nro_celular     VARCHAR(20)     NULL,
    user_telegram   VARCHAR(50)     NULL,
    is_admin        BOOLEAN         NOT NULL DEFAULT FALSE,
    ci              VARCHAR(20)     NULL UNIQUE,
    nombres         VARCHAR(100)    NOT NULL,
    apellidos       VARCHAR(100)    NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    last_login      TIMESTAMP       NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);
-- ============================================================
-- TABLA: CLIENTE
-- ============================================================
CREATE TABLE cliente (
    id_cliente      SERIAL          PRIMARY KEY,
    id_usuario      INT             NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    id_institucion  INT             NOT NULL REFERENCES institucion(id_institucion),
    username        VARCHAR(50)     NOT NULL UNIQUE,
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_agente_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    rol_institucion VARCHAR(50)     NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: AGENTE
-- ============================================================
CREATE TABLE agente (
    id_agente       SERIAL          PRIMARY KEY,
    id_usuario      INT             NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    username        VARCHAR(50)     NOT NULL UNIQUE,
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_agente_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);
-- ============================================================
-- TABLA: INSTITUCION
-- ============================================================
CREATE TABLE institucion (
    id_institucion  SERIAL          PRIMARY KEY,
    nombre          VARCHAR(255)    NOT NULL,
    descripcion     VARCHAR(50)     NULL
        CONSTRAINT chk_institucion_descripcion
            CHECK (descripcion IN ('hospital', 'colegio', 'laboratorio', 'otro')),
    direccion       TEXT            NULL,
    telefono        VARCHAR(20)     NULL,
    email           VARCHAR(255)    NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_institucion_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: SISTEMA
-- ============================================================
CREATE TABLE sistema (
    id_sistema      SERIAL          PRIMARY KEY,
    id_institucion  INT             NOT NULL REFERENCES institucion(id_institucion),
    nombre          VARCHAR(255)    NOT NULL,
    version         VARCHAR(50)     NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_sistema_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: INSTITUCION_SISTEMA
-- ============================================================
CREATE TABLE institucion_sistema (
    id_inst_sistema SERIAL          PRIMARY KEY,
    id_institucion  INT             NOT NULL REFERENCES institucion(id_institucion),
    id_sistema      INT             NOT NULL REFERENCES sistema(id_sistema),
    CONSTRAINT uq_inst_sistema UNIQUE (id_institucion, id_sistema)
);

-- ============================================================
-- TABLA: AREA
-- ============================================================
CREATE TABLE area (
    id_area         SERIAL          PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_area_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: HORARIO
-- ============================================================
CREATE TABLE horario (
    id_turno        SERIAL          PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL
        CONSTRAINT chk_horario_nombre
            CHECK (nombre IN ('Mañana', 'Tarde', 'Completo', 'Fin de semana', 'Personalizado')),
    hora_inicio     TIME            NOT NULL,
    hora_fin        TIME            NOT NULL,
    lunes           BOOLEAN         NOT NULL DEFAULT FALSE,
    martes          BOOLEAN         NOT NULL DEFAULT FALSE,
    miercoles       BOOLEAN         NOT NULL DEFAULT FALSE,
    jueves          BOOLEAN         NOT NULL DEFAULT FALSE,
    viernes         BOOLEAN         NOT NULL DEFAULT FALSE,
    sabado          BOOLEAN         NOT NULL DEFAULT FALSE,
    domingo         BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: CANAL_ENTRADA
-- ============================================================
CREATE TABLE canal_entrada (
    id_canal        SERIAL          PRIMARY KEY,
    nombre          VARCHAR(50)     NOT NULL
        CONSTRAINT chk_canal_nombre
            CHECK (nombre IN ('correo', 'whatsapp', 'telegram', 'formulario_web', 'chatbot_movil')),
    descripcion     TEXT            NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_canal_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);



-- ============================================================
-- TABLA: AGENTE_AREA
-- ============================================================
CREATE TABLE agente_area (
    id_agente_area  SERIAL          PRIMARY KEY,
    id_agente       INT             NOT NULL REFERENCES agente(id_agente),
    id_area         INT             NOT NULL REFERENCES area(id_area),
    asignado_en     TIMESTAMP       NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_agente_area UNIQUE (id_agente, id_area)
);

-- ============================================================
-- TABLA: AGENTE_HORARIO
-- ============================================================
CREATE TABLE agente_horario (
    id_agente_horario   SERIAL      PRIMARY KEY,
    id_agente           INT         NOT NULL REFERENCES agente(id_agente),
    id_turno            INT         NOT NULL REFERENCES horario(id_turno),
    vigente_desde       DATE        NOT NULL,
    vigente_hasta       DATE        NULL
);

-- ============================================================
-- TABLA: SOLICITUD
-- ============================================================
CREATE TABLE solicitud (
    id_solicitud    SERIAL          PRIMARY KEY,
    id_cliente      INT             NOT NULL REFERENCES cliente(id_cliente),
    id_canal        INT             NOT NULL REFERENCES canal_entrada(id_canal),
    id_sistema      INT             NOT NULL REFERENCES sistema(id_sistema),
    descripcion     TEXT            NOT NULL,
    received_at     TIMESTAMP       NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: ADJUNTO
-- ============================================================
CREATE TABLE adjunto (
    id_adjunto      SERIAL          PRIMARY KEY,
    id_solicitud    INT             NOT NULL REFERENCES solicitud(id_solicitud),
    subido_por      INT             NULL REFERENCES usuario(id_usuario),
    nombre_archivo  VARCHAR(255)    NOT NULL,
    url_archivo     VARCHAR(500)    NOT NULL,
    tamanio_bytes   INTEGER         NULL
        CONSTRAINT chk_adjunto_tamanio
            CHECK (tamanio_bytes IS NULL OR tamanio_bytes <= 10485760),
    uploaded_at     TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: TICKET
-- ============================================================
CREATE TABLE ticket (
    id_ticket               SERIAL          PRIMARY KEY,
    codigo_ticket           VARCHAR(20)     NOT NULL UNIQUE,
    id_solicitud            INT             NOT NULL REFERENCES solicitud(id_solicitud),
    id_area                 INT             NULL REFERENCES area(id_area),
    id_agente_asignado      INT             NULL REFERENCES agente(id_agente),
    id_agente_escalado      INT             NULL REFERENCES agente(id_agente),
    estado                  VARCHAR(15)     NOT NULL DEFAULT 'en_proceso'
        CONSTRAINT chk_ticket_estado
            CHECK (estado IN ('en_proceso', 'solucionado', 'cerrado', 'rechazado', 'escalado')),
    prioridad               VARCHAR(20)     NOT NULL DEFAULT 'medio'
        CONSTRAINT chk_ticket_prioridad
            CHECK (prioridad IN ('bajo', 'medio', 'alto')),
    motivo_escalamiento     VARCHAR(200)    NULL,
    fecha_primera_respuesta TIMESTAMP       NULL,
    fecha_solucionado       TIMESTAMP       NULL,
    fecha_cierre            TIMESTAMP       NULL,
    chatbot_enviado         BOOLEAN         NOT NULL DEFAULT FALSE,
    chatbot_resolvio        BOOLEAN         NOT NULL DEFAULT FALSE,
    horas_limite_confirmacion INT            NOT NULL DEFAULT 72, -- Configurable por el administrador (en horas)
    comentario_solucion     VARCHAR(500)    NOT NULL DEFAULT '',
    created_at              TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Si hay agente escalado, el motivo es obligatorio
    CONSTRAINT chk_ticket_escalamiento
        CHECK (
            id_agente_escalado IS NULL
            OR (id_agente_escalado IS NOT NULL AND motivo_escalamiento IS NOT NULL)
        )
);

-- ============================================================
-- TABLA: HISTORIAL_TICKET
-- ============================================================
CREATE TABLE historial_ticket (
    id_historial    SERIAL          PRIMARY KEY,
    id_ticket       INT             NOT NULL REFERENCES ticket(id_ticket),
    id_autor        INT             NULL REFERENCES usuario(id_usuario),
    tipo_evento     VARCHAR(50)     NOT NULL
        CONSTRAINT chk_historial_tipo_evento
            CHECK (tipo_evento IN (
                'TICKET_CREADO',
                'AGENTE_ASIGNADO',
                'ESTADO_CAMBIADO',
                'COMENTARIO_AGREGADO',
                'CONFIRMACION_CLIENTE',
                'TICKET_CERRADO',
                'REASIGNACION',
                'TICKET_ELIMINADO',
                'CAMBIO_PRIORIDAD'
            )),
    descripcion     TEXT            NOT NULL,
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: NOTIFICACION
-- ============================================================
CREATE TABLE notificacion (
    id_notificacion     SERIAL          PRIMARY KEY,
    id_ticket           INT             NOT NULL REFERENCES ticket(id_ticket),
    id_destinatario     INT             NOT NULL REFERENCES usuario(id_usuario),
    tipo_notificacion   VARCHAR(50)     NOT NULL
        CONSTRAINT chk_notificacion_tipo
            CHECK (tipo_notificacion IN ('ASIGNADO', 'SOLUCIONADO', 'RECHAZADO')),
    contenido           TEXT            NOT NULL,
    estado              VARCHAR(20)     NOT NULL DEFAULT 'pendiente'
        CONSTRAINT chk_notificacion_estado
            CHECK (estado IN ('pendiente', 'enviado', 'fallido')),
    sent_at             TIMESTAMP       NULL,
    error_log           TEXT            NULL,
    created_at          TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- ÍNDICES RECOMENDADOS
-- ============================================================

-- Ticket
CREATE INDEX idx_ticket_id_solicitud       ON ticket(id_solicitud);
CREATE INDEX idx_ticket_id_area            ON ticket(id_area);
CREATE INDEX idx_ticket_id_agente_asignado ON ticket(id_agente_asignado);
CREATE INDEX idx_ticket_estado             ON ticket(estado);
CREATE INDEX idx_ticket_prioridad          ON ticket(prioridad);
CREATE INDEX idx_ticket_created_at         ON ticket(created_at);

-- Solicitud
CREATE INDEX idx_solicitud_id_cliente      ON solicitud(id_cliente);
CREATE INDEX idx_solicitud_id_canal        ON solicitud(id_canal);
CREATE INDEX idx_solicitud_id_sistema      ON solicitud(id_sistema);

-- Historial
CREATE INDEX idx_historial_id_ticket       ON historial_ticket(id_ticket);
CREATE INDEX idx_historial_tipo_evento     ON historial_ticket(tipo_evento);

-- Notificación
CREATE INDEX idx_notificacion_id_ticket        ON notificacion(id_ticket);
CREATE INDEX idx_notificacion_id_destinatario  ON notificacion(id_destinatario);
CREATE INDEX idx_notificacion_estado           ON notificacion(estado);

-- Agente/Área/Horario
CREATE INDEX idx_agente_area_id_agente     ON agente_area(id_agente);
CREATE INDEX idx_agente_horario_id_agente  ON agente_horario(id_agente);

-- ============================================================
-- FUNCIÓN: actualizar updated_at automáticamente
-- ============================================================
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers updated_at
CREATE TRIGGER trg_usuario_updated_at
    BEFORE UPDATE ON usuario
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_institucion_updated_at
    BEFORE UPDATE ON institucion
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_sistema_updated_at
    BEFORE UPDATE ON sistema
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_area_updated_at
    BEFORE UPDATE ON area
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_horario_updated_at
    BEFORE UPDATE ON horario
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_cliente_updated_at
    BEFORE UPDATE ON cliente
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_agente_updated_at
    BEFORE UPDATE ON agente
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_ticket_updated_at
    BEFORE UPDATE ON ticket
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

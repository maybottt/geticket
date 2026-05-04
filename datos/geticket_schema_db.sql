-- ============================================================
-- GETICKET - Script Completo de Base de Datos
-- Motor: PostgreSQL 17
-- Estilo: snake_case
-- Formato timestamp: YYYY-MM-DD HH:MM:SS
-- Versión: 2.4 — incluye fecha_asignacion en ticket, triggers relacionados
-- ============================================================


-- ============================================================
-- TABLA: INSTITUCION
-- ============================================================
CREATE TABLE institucion (
    id_institucion  SERIAL          PRIMARY KEY,
    nombre          VARCHAR(255)    NOT NULL,
    tipo_institucion VARCHAR(50)    NULL
        CONSTRAINT chk_institucion_tipo
            CHECK (tipo_institucion IN ('hospital', 'colegio', 'laboratorio', 'otro')),
    descripcion     TEXT            NULL,
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
-- TABLA: USUARIO
-- ============================================================
CREATE TABLE usuario (
    id_usuario      SERIAL          PRIMARY KEY,
    username        VARCHAR(50)     NOT NULL UNIQUE,
    email           VARCHAR(255)    NOT NULL,
    password        VARCHAR(255)    NOT NULL,
    nro_celular     VARCHAR(20)     NULL,
    nro_celular_dos VARCHAR(20)     NULL,
    user_telegram   VARCHAR(50)     NULL,
    ci              VARCHAR(20)     NULL,
    nombres         VARCHAR(100)    NOT NULL,
    apellidos       VARCHAR(100)    NOT NULL,
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_usuario_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    last_login      TIMESTAMP       NULL,
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
    rol_institucion VARCHAR(50)     NOT NULL,
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_cliente_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: AGENTE
-- ============================================================
CREATE TABLE agente (
    id_agente       SERIAL          PRIMARY KEY,
    id_usuario      INT             NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_agente_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: ADMINISTRADOR
-- ============================================================
CREATE TABLE administrador (
    id_admin        SERIAL          PRIMARY KEY,
    id_usuario      INT             NOT NULL UNIQUE REFERENCES usuario(id_usuario),
    estado          VARCHAR(15)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_admin_estado
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
            CHECK (nombre IN ('correo', 'whatsapp', 'telegram', 'formulario_web', 'chatbot_movil', 'llamada')),
    descripcion     TEXT            NULL,
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_canal_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

-- ============================================================
-- TABLA: CATEGORIA_INCIDENCIA
-- ============================================================
CREATE TABLE categoria_incidencia (
    id_categoria    SERIAL          PRIMARY KEY,
    nombre          VARCHAR(100)    NOT NULL,
    descripcion     TEXT            NULL,
    id_area         INT             NULL REFERENCES area(id_area),
    estado          VARCHAR(20)     NOT NULL DEFAULT 'activo'
        CONSTRAINT chk_categoria_estado
            CHECK (estado IN ('activo', 'inactivo', 'eliminado')),
    created_at      TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_categoria_id_area ON categoria_incidencia(id_area);

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
-- TABLA: TICKET   (ahora con fecha_asignacion)
-- ============================================================
CREATE TABLE ticket (
    id_ticket               SERIAL          PRIMARY KEY,
    codigo_ticket           VARCHAR(20)     NOT NULL UNIQUE,
    id_cliente              INT             NOT NULL REFERENCES cliente(id_cliente),
    id_canal                INT             NOT NULL REFERENCES canal_entrada(id_canal),
    id_sistema              INT             NOT NULL REFERENCES sistema(id_sistema),
    id_categoria            INT             NULL REFERENCES categoria_incidencia(id_categoria),
    descripcion             TEXT            NOT NULL,
    received_at             TIMESTAMP       NULL,
    id_area                 INT             NULL REFERENCES area(id_area),
    id_agente_asignado      INT             NULL REFERENCES agente(id_agente),
    id_agente_escalado      INT             NULL REFERENCES agente(id_agente),
    fecha_asignacion        TIMESTAMP       NULL,   -- primera vez que se asignó un agente (se llena automáticamente por triggers)
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
    horas_limite_confirmacion INT           NOT NULL DEFAULT 72,
    comentario_solucion     TEXT            NOT NULL DEFAULT '',
    created_at              TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_ticket_escalamiento
        CHECK (
            id_agente_escalado IS NULL
            OR (id_agente_escalado IS NOT NULL AND motivo_escalamiento IS NOT NULL)
        )
);

-- ============================================================
-- TABLA: ADJUNTO
-- ============================================================
CREATE TABLE adjunto (
    id_adjunto      SERIAL          PRIMARY KEY,
    id_ticket       INT             NOT NULL REFERENCES ticket(id_ticket),
    subido_por      INT             NULL REFERENCES usuario(id_usuario),
    nombre_archivo  VARCHAR(255)    NOT NULL,
    url_archivo     VARCHAR(500)    NOT NULL,
    tamanio_bytes   INTEGER         NULL
        CONSTRAINT chk_adjunto_tamanio
            CHECK (tamanio_bytes IS NULL OR tamanio_bytes <= 10485760),
    uploaded_at     TIMESTAMP       NOT NULL DEFAULT NOW()
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
-- TABLA: SATISFACCION_TICKET   (encuesta CSAT)
-- ============================================================
CREATE TABLE satisfaccion_ticket (
    id_satisfaccion     SERIAL          PRIMARY KEY,
    id_ticket           INT             NOT NULL UNIQUE REFERENCES ticket(id_ticket),
    puntuacion          SMALLINT        NULL
        CONSTRAINT chk_satisfaccion_puntuacion
            CHECK (puntuacion IS NULL OR puntuacion BETWEEN 1 AND 5),
    comentario          TEXT            NULL,
    enviado_en          TIMESTAMP       NOT NULL DEFAULT NOW(),
    respondido_en       TIMESTAMP       NULL,

    CONSTRAINT chk_satisfaccion_fechas
        CHECK (respondido_en IS NULL OR enviado_en <= respondido_en)
);

-- ============================================================
-- ÍNDICES
-- ============================================================

-- Ticket
CREATE INDEX idx_ticket_id_cliente           ON ticket(id_cliente);
CREATE INDEX idx_ticket_id_canal             ON ticket(id_canal);
CREATE INDEX idx_ticket_id_sistema           ON ticket(id_sistema);
CREATE INDEX idx_ticket_id_categoria         ON ticket(id_categoria);
CREATE INDEX idx_ticket_id_area              ON ticket(id_area);
CREATE INDEX idx_ticket_id_agente_asignado   ON ticket(id_agente_asignado);
CREATE INDEX idx_ticket_estado               ON ticket(estado);
CREATE INDEX idx_ticket_prioridad            ON ticket(prioridad);
CREATE INDEX idx_ticket_created_at           ON ticket(created_at);

-- Adjunto
CREATE INDEX idx_adjunto_id_ticket           ON adjunto(id_ticket);

-- Historial
CREATE INDEX idx_historial_id_ticket         ON historial_ticket(id_ticket);
CREATE INDEX idx_historial_tipo_evento       ON historial_ticket(tipo_evento);

-- Notificación
CREATE INDEX idx_notificacion_id_ticket          ON notificacion(id_ticket);
CREATE INDEX idx_notificacion_id_destinatario    ON notificacion(id_destinatario);
CREATE INDEX idx_notificacion_estado             ON notificacion(estado);

-- Agente / Área / Horario
CREATE INDEX idx_agente_area_id_agente       ON agente_area(id_agente);
CREATE INDEX idx_agente_horario_id_agente    ON agente_horario(id_agente);

-- Cliente
CREATE INDEX idx_cliente_id_institucion      ON cliente(id_institucion);

-- Satisfacción
CREATE INDEX idx_satisfaccion_id_ticket      ON satisfaccion_ticket(id_ticket);
CREATE INDEX idx_satisfaccion_respondido     ON satisfaccion_ticket(respondido_en)
    WHERE respondido_en IS NOT NULL;
CREATE INDEX idx_satisfaccion_puntuacion     ON satisfaccion_ticket(puntuacion)
    WHERE puntuacion IS NOT NULL;


-- ============================================================
-- FUNCIÓN Y TRIGGERS: actualización automática de updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION fn_set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

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

CREATE TRIGGER trg_administrador_updated_at
    BEFORE UPDATE ON administrador
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_ticket_updated_at
    BEFORE UPDATE ON ticket
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();

CREATE TRIGGER trg_categoria_updated_at
    BEFORE UPDATE ON categoria_incidencia
    FOR EACH ROW EXECUTE FUNCTION fn_set_updated_at();


-- ============================================================
-- FUNCIONES Y TRIGGERS PARA FECHA_ASIGNACION
-- ============================================================

-- Triggers que actualizan fecha_asignacion cuando se asigna por primera vez un agente

-- Función para UPDATE: si el agente pasa de NULL a un valor concreto y fecha_asignacion aún es NULL, la establece
CREATE OR REPLACE FUNCTION fn_set_fecha_asignacion_update()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.id_agente_asignado IS NULL
       AND NEW.id_agente_asignado IS NOT NULL
       AND NEW.fecha_asignacion IS NULL THEN
        NEW.fecha_asignacion = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para UPDATE
CREATE TRIGGER trg_ticket_fecha_asignacion_upd
    BEFORE UPDATE ON ticket
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_fecha_asignacion_update();

-- Función para INSERT: si el ticket se crea con agente asignado, asigna la fecha de asignación automáticamente
CREATE OR REPLACE FUNCTION fn_set_fecha_asignacion_insert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id_agente_asignado IS NOT NULL AND NEW.fecha_asignacion IS NULL THEN
        NEW.fecha_asignacion = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para INSERT
CREATE TRIGGER trg_ticket_fecha_asignacion_ins
    BEFORE INSERT ON ticket
    FOR EACH ROW
    EXECUTE FUNCTION fn_set_fecha_asignacion_insert();
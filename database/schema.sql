-- Destruimos tablas existentes para asegurar una base limpia
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS blog_articulos;

-- Tabla de categorías
CREATE TABLE categorias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

-- Insertamos categorías base para las prácticas
INSERT INTO categorias (nombre, slug) VALUES ('Oficina', 'oficina');
INSERT INTO categorias (nombre, slug) VALUES ('Personas', 'personas');

-- Tabla de productos con vinculación a categorías
CREATE TABLE productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria_id INTEGER, -- Nueva columna para el enlace
    slug TEXT UNIQUE NOT NULL,           
    titulo TEXT NOT NULL,                
    pill_text TEXT,                      
    descripcion TEXT,                    
    showcase_1_titulo TEXT,
    showcase_1_texto TEXT,
    showcase_2_titulo TEXT,
    showcase_2_texto TEXT,
    caracteristicas_json TEXT,           
    integraciones_json TEXT,             
    seo_title TEXT,
    seo_description TEXT,
    ruta_carpeta TEXT NOT NULL,          
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(categoria_id) REFERENCES categorias(id)
);

-- Nueva tabla para los artículos del blog
CREATE TABLE blog_articulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    titulo TEXT NOT NULL,
    contenido TEXT NOT NULL,
    ruta_carpeta TEXT NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);
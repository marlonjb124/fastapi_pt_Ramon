# Prueba Técnica FastAPI

Este proyecto es una prueba técnica desarrollada con FastAPI, SQLAlchemy y Alembic. La idea es mostrar cómo estructuro una API moderna con autenticación, roles, visibilidad de recursos y operaciones CRUD completas.

## ¿Qué hace este proyecto?
- Permite crear usuarios, posts y tags.
- Soporta autenticación con JWT y control de acceso por roles (usuario gratis, usuario premium, admin).
- Los posts y tags pueden ser visibles o privados, y solo el dueño puede modificarlos o eliminarlos.
- Los administradores pueden ver y gestionar todos los recursos, incluidos los eliminados (soft delete).
- Los usuarios premium pueden acceder a posts de pago.
- Hay endpoints para vincular tags a posts y para restaurar recursos eliminados.

## ¿Cómo lo uso?
1. Clona el repo y entra a la carpeta del proyecto.
2. Si quieres, revisa el archivo `.env` para personalizar variables 
3. Levanta todo con Docker Compose:
   docker-compose up --build
4. Cuando todo esté arriba, abre tu navegador en http://localhost:8000/docs para ver y probar la API interactiva.
5. Ejecuta las migraciones con alembic upgrade head
  

## Usuarios de prueba
- Admin: admin@example.com / admin
- Puedes crear otros usuarios desde los endpoints de registro.

## Cosas útiles

- Si quieres probar los endpoints de admin o premium, cambia el rol del usuario desde el endpoint de admin (siendo admin).
- El soft delete permite recuperar posts y tags eliminados

## Creditos 
  En esta seccion quiero recomendar varios articulos proyectos y repositorios que me han servido de ayuda , no solo para esta PT sino para otros sistemas en los q he trabajado y me ha servidod e  experiencia.
  https://theshubhendra.medium.com/role-based-row-filtering-advanced-sqlalchemy-techniques-733e6b1328f6

  https://medium.com/@ramanbazhanau/mastering-sqlalchemy-a-comprehensive-guide-for-python-developers-ddb3d9f2e829

  https://github.com/fastapi/full-stack-fastapi-template
  (Usar para apoyarme en la implementacion emailchecking en el futuro)

  https://github.com/marlonjb124/Teams

  https://github.com/marlonjb124/N8N

  +Algunos proyectos locales





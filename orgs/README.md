# APP ORGS
## Los modelos que se crearan aca son:
- Direccion
- Departamento
- Cuadrilla
- Territorial
- Administrador (SECPLA)

## API REST
La app expone endpoints públicos (sin autenticación) bajo `/api/orgs/` utilizando **Django REST Framework**. Cada recurso mantiene las mismas reglas de negocio que las vistas tradicionales:

- `GET /api/orgs/direcciones/` — permite filtrar por `q`, `estado` (`activa`/`bloqueada`) y `responsable`. Incluye el equipo asociado y ofrece `POST/PUT/PATCH/DELETE` más la acción `POST /toggle-estado/`.
- `GET /api/orgs/departamentos/` — recibe filtros `q`, `estado` (`activo`/`bloqueado`) y `direccion`. Gestiona miembros y encargados mediante el campo `memberships`.
- `GET /api/orgs/cuadrillas/` — filtros `q`, `estado` y `departamento`; devuelve el departamento y los miembros actuales; admite la acción `POST /toggle-estado/`.
- `GET /api/orgs/territoriales/` — filtra por `q` en nombre o datos del responsable y permite asignar/quitar el perfil vinculado.

Para crear o actualizar miembros desde el frontend Angular basta con enviar una lista en `memberships`, por ejemplo:

```json
{
  "nombre": "Dirección de Obras",
  "estado": true,
  "memberships": [
    {"usuario_id": 5, "es_encargado": true},
    {"usuario_id": 12, "es_encargado": false}
  ]
}
```

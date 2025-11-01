# Arquitectura de Seguridad y Autorización

## Sistema de Dependencias Reutilizables

### Dependencias Base (app/core/deps.py)

```python
currentUserDep  # Usuario autenticado (cualquier rol)
sessionDep      # Sesión de base de datos
adminDep        # Solo usuarios ADMIN
premiumDep      # Solo usuarios PAID_USER o ADMIN
```

## Flujo de Autenticación y Autorización

### 1. Rutas Públicas
Sin `Depends()` - No requieren autenticación

### 2. Rutas Autenticadas
```python
@router.get("/endpoint")
async def endpoint(current_user: currentUserDep):
    # Usuario autenticado con cualquier rol
    # Los datos se filtran automáticamente según su rol
```

### 3. Rutas con Rol Específico
```python
@router.get("/admin/endpoint")
async def endpoint(admin_user: adminDep):
    # Solo ADMIN puede acceder
```

```python
@router.get("/premium/endpoint")
async def endpoint(premium_user: premiumDep):
    # Solo PAID_USER o ADMIN pueden acceder
```

## Filtrado Automático de Datos

### VisibilityMixin.apply_visibility_filters()

Filtra automáticamente según el rol del usuario:

**Usuario NO autenticado:**
- Solo ve contenido público y gratuito

**Usuario FREE_USER:**
- Ve contenido público gratuito
- Ve su propio contenido (público y privado)

**Usuario PAID_USER:**
- Todo lo de FREE_USER
- Ve contenido de pago de cualquier usuario

**Usuario ADMIN:**
- Ve todo el contenido (excepto eliminado)

## Ejemplos de Uso

### Listar Posts (filtrado automático)
```python
@router.get("/posts")
async def list_posts(db: sessionDep, current_user: currentUserDep):
    query = select(Post)
    query = VisibilityMixin.apply_visibility_filters(
        query,
        model_cls=Post,
        current_user_role=current_user.role,
        user_id=current_user.id
    )
    posts = await Post.execute_query(db, query)
    return posts
```

### Solo Admins
```python
@router.get("/admin/users")
async def list_users(db: sessionDep, admin: adminDep):
    # Solo ADMIN puede ejecutar esto
    return await User.get_all(db)
```

### Solo Premium
```python
@router.get("/premium/posts")
async def list_premium(db: sessionDep, premium: premiumDep):
    # Solo PAID_USER o ADMIN pueden acceder
    return await Post.filter(is_paid=True)
```

## Ventajas

✅ **DRY**: Sin código duplicado
✅ **Automático**: Filtrado por rol sin lógica manual
✅ **Seguro**: Control centralizado de permisos
✅ **Limpio**: Dependencias declarativas
✅ **Escalable**: Fácil agregar nuevos roles

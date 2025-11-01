"""
Script de prueba para endpoints de admin y premium
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"

async def test_endpoints():
    async with httpx.AsyncClient() as client:
        print("\n=== CREANDO USUARIOS ===")
        
        users = [
            {"email": "admin@test.com", "password": "admin123", "full_name": "Admin User"},
            {"email": "premium@test.com", "password": "premium123", "full_name": "Premium User"},
            {"email": "standard@test.com", "password": "standard123", "full_name": "Standard User"},
        ]
        
        for user in users:
            try:
                response = await client.post(f"{BASE_URL}/user/create-user", json=user)
                print(f"Usuario {user['email']}: {response.status_code}")
            except Exception as e:
                print(f"Error: {e}")
        
        print("\n=== LOGIN ADMIN ===")
        response = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "admin@test.com", "password": "admin123"}
        )
        if response.status_code == 200:
            admin_token = response.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            print(f"Token obtenido")
            
            print("\n=== LISTAR USUARIOS ===")
            response = await client.get(f"{BASE_URL}/admin/users", headers=admin_headers)
            if response.status_code == 200:
                users_list = response.json()
                print(f"Total usuarios: {len(users_list)}")
                for u in users_list:
                    print(f"  {u['email']}: {u['role']}")
                
                print("\n=== CAMBIAR ROL A PAID_USER ===")
                premium_user = next((u for u in users_list if u['email'] == "premium@test.com"), None)
                if premium_user:
                    response = await client.put(
                        f"{BASE_URL}/admin/users/{premium_user['id']}/role",
                        json={"role": "PAID_USER"},
                        headers=admin_headers
                    )
                    if response.status_code == 200:
                        print(f"Rol actualizado a: {response.json()['role']}")
                    else:
                        print(f"Error: {response.status_code}")
        else:
            print(f"Error login: {response.status_code}")
        
        print("\n=== LOGIN PREMIUM ===")
        response = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": "premium@test.com", "password": "premium123"}
        )
        if response.status_code == 200:
            premium_token = response.json()["access_token"]
            premium_headers = {"Authorization": f"Bearer {premium_token}"}
            print("Token obtenido")
            
            print("\n=== CREAR POST DE PAGO ===")
            post_data = {
                "title": "Curso Premium Python",
                "content": "Contenido exclusivo",
                "description": "Solo para premium",
                "category": "premium"
            }
            response = await client.post(
                f"{BASE_URL}/posts/",
                json=post_data,
                headers=premium_headers
            )
            if response.status_code == 201:
                post = response.json()
                post_id = post["id"]
                print(f"Post creado: ID {post_id}")
                
                print("\n=== CAMBIAR A POST DE PAGO ===")
                response = await client.put(
                    f"{BASE_URL}/premium/posts/{post_id}/toggle-paid?is_paid=true",
                    headers=premium_headers
                )
                print(f"Status: {response.status_code}")
                
                print("\n=== LISTAR POSTS PREMIUM ===")
                response = await client.get(f"{BASE_URL}/premium/posts", headers=premium_headers)
                if response.status_code == 200:
                    print(f"Posts de pago: {len(response.json())}")
            else:
                print(f"Error: {response.status_code} - {response.json()}")
        else:
            print(f"Error login: {response.status_code}")

if __name__ == "__main__":
    print("=== PRUEBAS ADMIN Y PREMIUM ===")
    asyncio.run(test_endpoints())
    print("\n=== COMPLETADO ===")

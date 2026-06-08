/**
 * Edge Function: user-admin (v7 pattern)
 * 
 * Gestión de usuarios (crear, reset password, eliminar) desde el frontend.
 * Usa service_role key server-side; verifica que el caller sea admin.
 * 
 * Deploy: mcp_supabase_deploy_edge_function(name='user-admin', verify_jwt=false)
 *   verify_jwt=false porque la función hace su propia verificación de admin
 *   internamente (getUser + role check). verify_jwt=true causa 500 cuando
 *   hay auth duplicada (gateway + función). Ver references/edge-function-cors.md
 * 
 * Prerequisitos en DB:
 *   - Tabla `profiles` con columna `role` (incluye 'admin')
 *   - Function `fix_user_null_columns(user_email text)` RPC
 * 
 * Acciones: create-user, reset-password, delete-user
 * 
 * CORS: Allowlist dinámica — lee el header Origin de cada request y solo
 *   permite dominios conocidos. Más seguro que Access-Control-Allow-Origin: *
 *   Ver references/edge-function-cors.md sección "Allowlist dinámica"
 * 
 * Errores: Todos los mensajes de error se retornan en español en el body JSON
 *   como { error: "mensaje" }. El frontend usa extractFnError() para extraerlos.
 * 
 * Llamada desde frontend:
 *   const { error } = await supabase.functions.invoke('user-admin', {
 *     body: { action: 'create-user', username, password, role: 'lider', profile: {...} }
 *   })
 *   const { error } = await supabase.functions.invoke('user-admin', {
 *     body: { action: 'reset-password', authId: user.auth_id, newPassword: '...' }
 *   })
 *   const { error } = await supabase.functions.invoke('user-admin', {
 *     body: { action: 'delete-user', authId: user.auth_id }
 *   })
 */

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// Admin client — bypasses RLS, uses service_role key
const adminClient = createClient(supabaseUrl, serviceRoleKey, {
  auth: { autoRefreshToken: false, persistSession: false },
});

// --- CORS Allowlist ---
// Reemplazar <app-domain> con el dominio real del proyecto.
const ALLOWED_ORIGINS = [
  "https://<app-domain>.pages.dev",
  "http://localhost:5173",
];

function getAllowedOrigin(req: Request): string | null {
  const origin = req.headers.get("Origin");
  if (!origin) return null;
  if (ALLOWED_ORIGINS.includes(origin)) return origin;
  // Cloudflare Pages preview deployments: <hash>.<app-domain>.pages.dev
  if (origin.endsWith(".<app-domain>.pages.dev")) return origin;
  return null;
}

Deno.serve(async (req: Request) => {
  // --- CORS dinámico per-request ---
  const origin = getAllowedOrigin(req);
  const corsHeaders: Record<string, string> = origin
    ? {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers":
          "authorization, x-client-info, apikey, content-type",
      }
    : {};

  function json(data: unknown, status = 200) {
    return new Response(JSON.stringify(data), {
      status,
      headers: {
        "Content-Type": "application/json",
        "Connection": "keep-alive",
        ...corsHeaders,
      },
    });
  }

  // CORS preflight — reject unknown origins with 403
  if (req.method === "OPTIONS") {
    if (!origin) return new Response(null, { status: 403 });
    return new Response(null, { status: 204, headers: corsHeaders });
  }

  if (req.method !== "POST") {
    return json({ error: "Method not allowed" }, 405);
  }

  try {
    const authHeader = req.headers.get("Authorization");
    const anonKey = req.headers.get("apikey");

    if (!authHeader || !anonKey) {
      return json({ error: "Faltan credenciales de autenticación" }, 401);
    }

    // Verify caller is authenticated
    const userClient = createClient(supabaseUrl, anonKey, {
      global: { headers: { Authorization: authHeader } },
      auth: { autoRefreshToken: false, persistSession: false },
    });

    const { data: { user }, error: userErr } = await userClient.auth.getUser();
    if (userErr || !user) {
      return json({ error: "Sesión expirada — vuelve a iniciar sesión" }, 401);
    }

    // Verify admin role
    const { data: profile, error: profileErr } = await userClient
      .from("profiles")
      .select("role")
      .eq("auth_id", user.id)
      .single();

    if (profileErr || !profile) {
      return json({ error: "No se pudo verificar tu perfil" }, 403);
    }

    if (profile.role !== "admin") {
      return json({ error: "Acceso denegado — solo administradores" }, 403);
    }

    const body = await req.json();
    const { action } = body;

    switch (action) {
      case "create-user": {
        const { username, password, role, profile: profileData } = body;
        const email = `${username}@<app-domain>.local`;

        const { data: authData, error: authError } =
          await adminClient.auth.admin.createUser({
            email,
            password,
            email_confirm: true,
          });

        if (authError) {
          return json({ error: `Error al crear usuario: ${authError.message}` }, 400);
        }

        const { error: profileError } = await adminClient
          .from("profiles")
          .insert({
            auth_id: authData.user.id,
            username,
            nombre: profileData.nombre,
            // ... campos del perfil
            role,
          });

        if (profileError) {
          // Rollback: delete auth user if profile insert failed
          await adminClient.auth.admin.deleteUser(authData.user.id);
          return json({ error: `Error al crear perfil: ${profileError.message}` }, 400);
        }

        // Fix GoTrue NULL string columns (best effort)
        try {
          await adminClient.rpc("fix_user_null_columns", { user_email: email });
        } catch {
          // Non-critical
        }

        return json({ ok: true, userId: authData.user.id, username });
      }

      case "reset-password": {
        const { authId, newPassword } = body;
        if (!authId || !newPassword) {
          return json({ error: "Faltan datos: authId y newPassword son obligatorios" }, 400);
        }
        const { error: updateError } =
          await adminClient.auth.admin.updateUserById(authId, { password: newPassword });
        if (updateError) {
          return json({ error: `Error al actualizar contraseña: ${updateError.message}` }, 400);
        }
        return json({ ok: true });
      }

      case "delete-user": {
        const { authId } = body;
        if (!authId) {
          return json({ error: "Falta el ID del usuario a eliminar" }, 400);
        }
        const { error: deleteError } =
          await adminClient.auth.admin.deleteUser(authId);
        if (deleteError) {
          return json({ error: `Error al eliminar usuario: ${deleteError.message}` }, 400);
        }
        return json({ ok: true });
      }

      default:
        return json({ error: `Acción desconocida: ${action}` }, 400);
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return json({ error: `Error interno del servidor: ${message}` }, 500);
  }
});

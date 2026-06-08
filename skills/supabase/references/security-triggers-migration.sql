-- =====================================================================
-- Defense-in-depth security triggers for Supabase projects
-- Applied via: mcp_supabase_apply_migration
-- =====================================================================

-- SEC1: Prevent role escalation by non-admin users
create or replace function prevent_role_escalation()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  -- If role is changing and current user is NOT admin → block
  if old.role is distinct from new.role then
    if get_user_role() != 'admin' then
      raise exception 'No tienes permisos para cambiar roles de usuario';
    end if;
  end if;
  return new;
end;
$$;

drop trigger if exists trg_prevent_role_escalation on profiles;
create trigger trg_prevent_role_escalation
  before update on profiles
  for each row
  execute function prevent_role_escalation();

-- SEC2: Prevent creating admin profiles without auth_id
create or replace function prevent_orphan_admin_profiles()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  if new.role = 'admin' and new.auth_id is null then
    raise exception 'No se puede crear perfil de administrador sin usuario de autenticación asociado';
  end if;
  return new;
end;
$$;

drop trigger if exists trg_prevent_orphan_admin on profiles;
create trigger trg_prevent_orphan_admin
  before insert on profiles
  for each row
  execute function prevent_orphan_admin_profiles();

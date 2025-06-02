// Fetch all roles (role, description)
export async function fetchRoles() {
  // These are static for now, but could be fetched from config/help endpoint
  return [
    { role: "superadmin", description: "Full access to all bot and config features" },
    { role: "admin", description: "Can manage most config, users, and moderate" },
    { role: "user", description: "Basic access to bot features" },
  ];
}

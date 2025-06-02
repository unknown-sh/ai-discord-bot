// Role checking utility
const roleTier = { guest: 0, user: 1, admin: 2, superadmin: 3 };
module.exports = function hasRole(userRole, minRole) {
  return roleTier[userRole] >= roleTier[minRole];
};

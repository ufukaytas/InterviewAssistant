using Auth.Application.Interfaces;
using Auth.Domain.Entities;
using Auth.Infrastructure.Contexts;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Repositories
{
    public class RoleRepository : IRoleRepository
    {
        private readonly AuthDbContext _context;

        public RoleRepository(AuthDbContext context)
        {
            _context = context;
        }

        public async Task<Role?> GetRoleNameAsync(string roleName)
        {
            return await _context.Roles.FirstOrDefaultAsync(x => x.RoleName == roleName);
        }
    }
}

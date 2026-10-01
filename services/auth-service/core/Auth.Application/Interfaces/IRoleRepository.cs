using Auth.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IRoleRepository
    {
        Task<Role?> GetRoleNameAsync(string roleName);
    }
}

using Auth.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IUserRepository
    {
        Task AddAsync(User user);
        bool Update(User user);
        Task<User?> GetUserByEmailAsync(string email);
        Task<User?> GetUserByIdAsync(Guid userId);
        Task<bool> ExistsUserByEmailAsync(string email);
    }
}

using Auth.Application.Interfaces;
using Auth.Infrastructure.Contexts;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Security
{
    public class PasswordHasher : IPasswordHasher
    {
        private readonly AuthDbContext _context;

        public PasswordHasher(AuthDbContext context)
        {
            _context = context;
        }

        public string Hash(string password)
        {
            return BCrypt.Net.BCrypt.HashPassword(password);
        }

        public bool Verify(string password, string passwordHash)
        {
            return BCrypt.Net.BCrypt.Verify(password, passwordHash);
        }
    }
}

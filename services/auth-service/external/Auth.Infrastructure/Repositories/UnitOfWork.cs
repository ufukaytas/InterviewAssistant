using Auth.Application.Interfaces;
using Auth.Infrastructure.Contexts;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Repositories
{
    public class UnitOfWork : IUnitOfWork
    {
        private readonly AuthDbContext _context;

        public UnitOfWork(AuthDbContext context)
        {
            _context = context;
        }

        public Task<int> SaveChangesAsync()
        {
            return _context.SaveChangesAsync();
        }
    }
}

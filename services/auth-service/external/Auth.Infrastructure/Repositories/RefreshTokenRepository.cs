using Auth.Application.Interfaces;
using Auth.Domain.Entities;
using Auth.Infrastructure.Contexts;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.ChangeTracking;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Repositories
{
    public class RefreshTokenRepository : IRefreshTokenRepository
    {
        private readonly AuthDbContext _context;

        public RefreshTokenRepository(AuthDbContext context)
        {
            _context = context;
        }

        public async Task AddAsync(RefreshToken refreshToken)
        {
            await _context.RefreshTokens.AddAsync(refreshToken);
        }

        public async Task<RefreshToken?> GetRefreshTokenAsync(string token)
        {
            return await _context.RefreshTokens
                .Include(x => x.User)
                .FirstOrDefaultAsync(x => x.Token == token);
        }

        public bool Remove(RefreshToken refreshToken)
        {
            EntityEntry<RefreshToken> entityEntry = _context.RefreshTokens.Remove(refreshToken);
            return entityEntry.State == EntityState.Deleted;
        }

        public bool Update(RefreshToken refreshToken)
        {
            EntityEntry<RefreshToken> entityEntry = _context.RefreshTokens.Update(refreshToken);
            return entityEntry.State == EntityState.Modified;
        }
    }
}

using Auth.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IRefreshTokenRepository
    {
        Task<RefreshToken?> GetRefreshTokenAsync(string token);
        Task AddAsync(RefreshToken refreshToken);
        bool Update(RefreshToken refreshToken);
    }
}

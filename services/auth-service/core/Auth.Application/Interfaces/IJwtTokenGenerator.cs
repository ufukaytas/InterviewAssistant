using Auth.Application.DTOs;
using Auth.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IJwtTokenGenerator
    {
        TokenDto GenerateAccessToken(User user);

        //v2 için role 
        //string GenerateAccessToken(User user, IList<string> Roles);
        string GenerateRefreshToken();

    }
}

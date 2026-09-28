using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Login
{
    public class LoginCommandResponse
    {
        public string AccessToken { get; set; } = null!;
        public DateTime AccessTokenExpiration { get; set; }
        public string RefreshToken { get; set; } = null!;
    }
}

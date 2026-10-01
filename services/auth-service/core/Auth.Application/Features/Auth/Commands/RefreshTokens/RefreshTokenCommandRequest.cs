using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.RefreshTokens
{
    public class RefreshTokenCommandRequest : IRequest<CustomResponseDto<RefreshTokenCommandResponse>>
    {
        public string AccessToken { get; set; } = null!;
        public string RefreshToken { get; set; } = null!;
    }
}

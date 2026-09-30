using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Serialization;

namespace Auth.Application.Features.Auth.Commands.Logout
{
    public class LogoutCommandRequest : IRequest<CustomResponseDto>
    {
        public string RefreshToken { get; set; } = null!;
    }
}

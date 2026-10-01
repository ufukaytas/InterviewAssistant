using Auth.Application.DTOs;
using Auth.Application.Features.Auth.Commands.Common;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Register
{
    public class RegisterCommandRequest : IRequest<CustomResponseDto>
    {
        public string FirstName { get; set; } = null!;
        public string LastName { get; set; } = null!;
        public string Email { get; set; } = null!;
        public string Password { get; set; } = null!;
    }
}

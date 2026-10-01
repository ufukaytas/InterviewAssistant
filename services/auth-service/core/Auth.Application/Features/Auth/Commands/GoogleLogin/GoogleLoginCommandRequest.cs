using Auth.Application.DTOs;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.GoogleLogin
{
    public class GoogleLoginCommandRequest : IRequest<CustomResponseDto<GoogleLoginCommandResponse>>
    {
        public string IdToken { get; set; } = null!;
    }
}

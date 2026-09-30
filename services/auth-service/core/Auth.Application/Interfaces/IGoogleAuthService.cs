using Auth.Application.DTOs;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Interfaces
{
    public interface IGoogleAuthService
    {
        Task<GoogleUserProfileDto> VerifyGoogleTokenAsync(string idToken);
    }
}

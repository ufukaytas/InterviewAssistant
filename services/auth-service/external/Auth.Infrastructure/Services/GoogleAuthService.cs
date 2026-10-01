using Auth.Application.DTOs;
using Auth.Application.Exceptions;
using Auth.Application.Interfaces;
using Google.Apis.Auth;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Infrastructure.Services
{
    public class GoogleAuthService : IGoogleAuthService
    {
        private readonly IConfiguration _configuration;

        public GoogleAuthService(IConfiguration configuration)
        {
            _configuration = configuration;
        }

        public async Task<GoogleUserProfileDto> VerifyGoogleTokenAsync(string idToken)
        {
            try
            {
                var settings = new GoogleJsonWebSignature.ValidationSettings()
                {
                    Audience = new[] { _configuration["Google:ClientId"] }
                };

                // token google kütüphanesi tarafından doğrulanır ve çözülür.
                var payload = await GoogleJsonWebSignature.ValidateAsync(idToken, settings);

                return new GoogleUserProfileDto
                {
                    Email = payload.Email,
                    FirstName = payload.GivenName ?? "",
                    LastName = payload.FamilyName ?? ""
                };
            }
            catch (InvalidJwtException)
            {
                throw new BusinessException("Geçersiz veya süresi dolmuş Google token'ı.");
            }
        }
    }
}

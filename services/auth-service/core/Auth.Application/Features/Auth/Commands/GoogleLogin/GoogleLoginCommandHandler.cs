using Auth.Application.DTOs;
using Auth.Application.Interfaces;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.GoogleLogin
{
    internal class GoogleLoginCommandHandler : IRequestHandler<GoogleLoginCommandRequest, CustomResponseDto<GoogleLoginCommandResponse>>
    {
        private readonly IGoogleAuthService _googleAuthService;
        private readonly IUserRepository _userRepository;
        private readonly IJwtTokenGenerator _jwtTokenGenerator;
        private readonly IUnitOfWork _unitOfWork;

        public GoogleLoginCommandHandler(IGoogleAuthService googleAuthService, IUserRepository userRepository, IJwtTokenGenerator jwtTokenGenerator, IUnitOfWork unitOfWork)
        {
            _googleAuthService = googleAuthService;
            _userRepository = userRepository;
            _jwtTokenGenerator = jwtTokenGenerator;
            _unitOfWork = unitOfWork;
        }

        public async Task<CustomResponseDto<GoogleLoginCommandResponse>> Handle(GoogleLoginCommandRequest request, CancellationToken cancellationToken)
        {
            // google tokenını doğrula ve bilgileri al
            var googleUser = await _googleAuthService.VerifyGoogleTokenAsync(request.IdToken);

            var user = await _userRepository.GetUserByEmailAsync(googleUser.Email);

            if(user == null)
            {
                user = new Domain.Entities.User
                {
                    Email = googleUser.Email,
                    FirstName = googleUser.FirstName,
                    LastName = googleUser.LastName,
                    // google ile girenlerin sifresi olmaz. (null veya güçlü bir hash oluşturulabilir)
                    PasswordHash = Guid.NewGuid().ToString(),
                };

                await _userRepository.AddAsync(user);
                await _unitOfWork.SaveChangesAsync();
            }

            var tokenDto = _jwtTokenGenerator.GenerateAccessToken(user);

            var response = new GoogleLoginCommandResponse
            {
                AccessToken = tokenDto.AccessToken,
                AccessTokenExpiration = tokenDto.AccessTokenExpiration,
                RefreshToken = tokenDto.RefreshToken,
            };

            return CustomResponseDto<GoogleLoginCommandResponse>.Success(200, response, "Google girişi başarılı");
        }
    }
}

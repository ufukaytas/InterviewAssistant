using Auth.Application.DTOs;
using Auth.Application.Interfaces;
using Auth.Application.Exceptions;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;
using Auth.Domain.Entities;

namespace Auth.Application.Features.Auth.Commands.Login
{
    internal class LoginCommandHandler : IRequestHandler<LoginCommandRequest, CustomResponseDto<LoginCommandResponse>>
    {
        private readonly IUnitOfWork _unitOfWork;
        private readonly IUserRepository _userRepository;
        private readonly IPasswordHasher _hasher;
        private readonly IJwtTokenGenerator _jwtTokenGenerator;
        private readonly IRefreshTokenRepository _refreshTokenRepository;

        public LoginCommandHandler(IUnitOfWork unitOfWork, IUserRepository userRepository, IPasswordHasher hasher, IJwtTokenGenerator jwtTokenGenerator, IRefreshTokenRepository refreshTokenRepository)
        {
            _unitOfWork = unitOfWork;
            _userRepository = userRepository;
            _hasher = hasher;
            _jwtTokenGenerator = jwtTokenGenerator;
            _refreshTokenRepository = refreshTokenRepository;
        }

        public async Task<CustomResponseDto<LoginCommandResponse>> Handle(LoginCommandRequest request, CancellationToken cancellationToken)
        {
            var user = await _userRepository.GetUserByEmailAsync(request.Email);

            if (user == null || !_hasher.Verify(request.Password, user.PasswordHash))
                throw new AuthenticationException("Email veya şifre hatalı");

            if (!user.IsActive)
                throw new BusinessException("Hesabınız devre dışı");

            var tokenDto = _jwtTokenGenerator.GenerateAccessToken(user);

            var refreshToken = new RefreshToken
            {
                UserId = user.Id,
                Token = tokenDto.RefreshToken,
                AccessToken = tokenDto.AccessToken,
                ExpiresDate = DateTime.UtcNow.AddDays(7)
            };

            await _refreshTokenRepository.AddAsync(refreshToken);
            await _unitOfWork.SaveChangesAsync();

            var responseData = new LoginCommandResponse
            {
                AccessToken = tokenDto.AccessToken,
                AccessTokenExpiration = tokenDto.AccessTokenExpiration,
                RefreshToken = tokenDto.RefreshToken
            };

            return CustomResponseDto<LoginCommandResponse>.Success(200, responseData,"Giriş başarılı");
        }
    }
}

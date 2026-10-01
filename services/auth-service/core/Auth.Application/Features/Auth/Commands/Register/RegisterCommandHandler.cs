using Auth.Application.DTOs;
using Auth.Application.Exceptions;
using Auth.Application.Features.Auth.Commands.Common;
using Auth.Application.Interfaces;
using Auth.Domain.Entities;
using AutoMapper;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Features.Auth.Commands.Register
{
    internal class RegisterCommandHandler : IRequestHandler<RegisterCommandRequest, CustomResponseDto>
    {
        private readonly IUserRepository _userRepository;
        private readonly IPasswordHasher _hasher;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IMapper _mapper;

        public RegisterCommandHandler(IUserRepository userRepository, IMapper mapper, IPasswordHasher hasher, IUnitOfWork unitOfWork)
        {
            _userRepository = userRepository;
            _mapper = mapper;
            _hasher = hasher;
            _unitOfWork = unitOfWork;
        }

        public async Task<CustomResponseDto> Handle(RegisterCommandRequest request, CancellationToken cancellationToken)
        {
            var isEmailExist = await _userRepository.ExistsUserByEmailAsync(request.Email);
            if (isEmailExist == true)
                throw new BusinessException("Email sistemde kayıtlı");

            var passwordHash = _hasher.Hash(request.Password);

            var user = _mapper.Map<User>(request);
            user.PasswordHash = passwordHash;
            await _userRepository.AddAsync(user);
            await _unitOfWork.SaveChangesAsync();

            return CustomResponseDto.Success(200, "Kayıt başarılı");
        }

    }
}

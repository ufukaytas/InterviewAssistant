using FluentValidation;
using MediatR;
using System;
using System.Collections.Generic;
using System.Text;

namespace Auth.Application.Behaviors
{
    public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    {
        private readonly IEnumerable<IValidator<TRequest>> _validators;

        public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        {
            _validators = validators;
        }

        public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
        {
            // kural yoksa geç handler'a yolla
            if (!_validators.Any())
                return await next();

            // kuralları çalıştır ve hataları topla
            var context = new ValidationContext<TRequest>(request);
            var validationResults = await Task.WhenAll(_validators.Select(v => v.ValidateAsync(context, cancellationToken)));

            // içinde hata olanları ayıkla
            var errors = validationResults
                .SelectMany(r => r.Errors)
                .Where(f => f != null)
                .GroupBy(x => x.PropertyName, x => x.ErrorMessage)
                .ToDictionary(g => g.Key, g => g.ToArray());

            // hata varsa ValidationException fırlat
            if (errors.Any())
                throw new Exceptions.ValidationException(errors);

            return await next();


        }
    }
}

FROM public.ecr.aws/lambda/python:3.8

# install dependecies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --pre gql[all] --target "${LAMBDA_TASK_ROOT}" && \
    pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# copy code
COPY src .

CMD ["main.handle_campaign"]
package ru.itis.crawler.dto;

import io.quarkus.runtime.annotations.RegisterForReflection;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.eclipse.microprofile.openapi.annotations.media.Schema;
import org.jboss.resteasy.annotations.providers.multipart.PartType;

import javax.ws.rs.FormParam;
import javax.ws.rs.core.MediaType;

@Builder
@Data
@AllArgsConstructor
@NoArgsConstructor
@RegisterForReflection
public class FileDTO {

    private String name;

    @FormParam("file")
    @Schema(description = "Файл в формате .txt, где содержится список ссылок для скачивания страниц")
    @PartType(MediaType.APPLICATION_OCTET_STREAM)
    private byte[] file;
}

package ru.itis.crawler;

import io.quarkus.runtime.annotations.RegisterForReflection;
import lombok.extern.slf4j.Slf4j;
import org.jboss.resteasy.annotations.providers.multipart.MultipartForm;
import ru.itis.crawler.dto.FileDTO;
import ru.itis.crawler.service.CrawlerService;

import javax.inject.Inject;
import javax.ws.rs.Consumes;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.core.HttpHeaders;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

@Slf4j
@Path("/crawler")
@RegisterForReflection
public class CrawlerResource {

    private final String CONTENT_DISPOSITION = "attachment; filename=\"%s\"";

    @Inject
    CrawlerService crawlerService;

    @POST
    @Consumes(MediaType.MULTIPART_FORM_DATA)
    public Response download(@MultipartForm FileDTO fileDTO) {
        var file = crawlerService.download(fileDTO);
        return Response.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, String.format(CONTENT_DISPOSITION, file.getName()))
                .entity(file.getFile())
                .build();
    }
}
